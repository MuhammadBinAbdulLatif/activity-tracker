import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.utils import timezone
from .models import AudiobookEntry, AudiobookStatus
from services.audiobook_service import audiobook_service

@login_required
def audiobook_list_view(request):
    """
    Renders the dedicated Audiobooks section categorized by Currently Listening,
    Listening Wishlist (Plan to Listen), and Completed / Library.
    """
    entries = AudiobookEntry.objects.filter(user=request.user)

    listening = entries.filter(status=AudiobookStatus.LISTENING)
    wishlist = entries.filter(status=AudiobookStatus.PLAN_TO_LISTEN)
    completed = entries.filter(status=AudiobookStatus.COMPLETED)
    dropped = entries.filter(status=AudiobookStatus.DROPPED)

    context = {
        "listening": listening,
        "wishlist": wishlist,
        "completed": completed,
        "dropped": dropped,
        "total_count": entries.count(),
        "status_choices": AudiobookStatus.choices,
    }
    return render(request, "audiobooks/list.html", context)

@login_required
def search_audiobooks_view(request):
    """
    Live HTMX or JSON search for audiobooks via iTunes API.
    Excludes DROPPED and deleted items from is_tracked.
    """
    query = request.GET.get("q", "").strip()
    if not query:
        return render(request, "audiobooks/partials/search_results.html", {"results": []})

    data = audiobook_service.search_audiobooks(query, limit=10)
    results = data.get("results", [])

    # Exclude DROPPED from active tracked items
    tracked_external_ids = set(
        AudiobookEntry.objects.filter(user=request.user, external_id__gt="")
        .exclude(status=AudiobookStatus.DROPPED)
        .values_list("external_id", flat=True)
    )

    formatted_results = []
    for item in results:
        ext_id = item.get("external_id", "")
        duration_mins = item.get("duration_minutes") or 0
        hours = duration_mins // 60
        mins = duration_mins % 60
        if hours > 0 and mins > 0:
            duration_str = f"{hours}h {mins}m"
        elif hours > 0:
            duration_str = f"{hours}h"
        elif mins > 0:
            duration_str = f"{mins}m"
        else:
            duration_str = ""

        formatted_results.append({
            "external_id": ext_id,
            "title": item.get("title"),
            "author": item.get("author"),
            "narrator": item.get("narrator"),
            "duration_minutes": duration_mins,
            "duration_display": duration_str,
            "cover_url": item.get("cover_url") or "",
            "preview_audio_url": item.get("preview_audio_url") or "",
            "release_year": item.get("release_year") or "",
            "genre": item.get("genre") or "",
            "description": item.get("description") or "",
            "is_tracked": ext_id in tracked_external_ids if ext_id else False,
        })

    if request.headers.get("HX-Request"):
        return render(request, "audiobooks/partials/search_results.html", {"results": formatted_results})
    return JsonResponse({"results": formatted_results})

@login_required
def add_audiobook_view(request):
    """
    Tracks an audiobook from search or via custom manual entry.
    """
    if request.method == "POST":
        external_id = request.POST.get("external_id", "").strip()
        title = request.POST.get("title", "").strip()
        author = request.POST.get("author", "").strip()
        narrator = request.POST.get("narrator", "").strip() or "Narrator Unlisted"
        cover_url = request.POST.get("cover_url", "").strip()
        preview_audio_url = request.POST.get("preview_audio_url", "").strip()
        genre = request.POST.get("genre", "").strip()
        description = request.POST.get("description", "").strip()
        release_year = request.POST.get("release_year") or None
        status = request.POST.get("status", AudiobookStatus.PLAN_TO_LISTEN)
        
        # Duration calculation
        duration_minutes_direct = request.POST.get("duration_minutes")
        if duration_minutes_direct:
            total_duration = max(int(duration_minutes_direct), 0)
        else:
            duration_hours = int(request.POST.get("duration_hours") or 0)
            duration_mins = int(request.POST.get("duration_mins") or 0)
            total_duration = (duration_hours * 60) + duration_mins
        
        rating = request.POST.get("rating") or None
        narrator_rating = request.POST.get("narrator_rating") or None
        review = request.POST.get("review", "").strip()
        mind_changing = request.POST.get("mind_changing_takeaways", "").strip()
        quotes = request.POST.get("favorite_quotes", "").strip()
        playback_speed = float(request.POST.get("playback_speed") or 1.00)

        # Initial dates
        start_date = timezone.now().date() if status == AudiobookStatus.LISTENING else None
        finish_date = timezone.now().date() if status == AudiobookStatus.COMPLETED else None

        if external_id:
            entry, created = AudiobookEntry.objects.update_or_create(
                user=request.user,
                external_id=external_id,
                defaults={
                    "title": title or "Untitled Audiobook",
                    "author": author,
                    "narrator": narrator,
                    "cover_url": cover_url,
                    "preview_audio_url": preview_audio_url,
                    "genre": genre,
                    "description": description,
                    "release_year": int(release_year) if release_year else None,
                    "duration_minutes": total_duration,
                    "status": status,
                    "playback_speed": playback_speed,
                    "rating": float(rating) if rating else None,
                    "narrator_rating": float(narrator_rating) if narrator_rating else None,
                    "review": review,
                    "mind_changing_takeaways": mind_changing,
                    "favorite_quotes": quotes,
                    "start_date": start_date,
                    "finish_date": finish_date,
                }
            )
            action = "Added" if created else "Updated"
            messages.success(request, f"{action} '{entry.title}' to your Audiobook chronicle.")
            return redirect("audiobook_detail", audiobook_id=entry.id)

        # Manual Entry Fallback
        if title:
            custom_cover = request.FILES.get("cover_file")
            entry = AudiobookEntry.objects.create(
                user=request.user,
                title=title,
                author=author,
                narrator=narrator,
                custom_cover=custom_cover,
                duration_minutes=total_duration,
                genre=genre,
                description=description,
                release_year=int(release_year) if release_year else None,
                status=status,
                playback_speed=playback_speed,
                rating=float(rating) if rating else None,
                narrator_rating=float(narrator_rating) if narrator_rating else None,
                review=review,
                mind_changing_takeaways=mind_changing,
                favorite_quotes=quotes,
                start_date=start_date,
                finish_date=finish_date,
                is_custom=True,
            )
            messages.success(request, f"Created custom audiobook '{entry.title}'.")
            return redirect("audiobook_detail", audiobook_id=entry.id)

    return redirect("audiobook_list")

@login_required
def audiobook_detail_view(request, audiobook_id):
    """
    Renders the immersive Audiobook Sanctuary detail view:
    Square cover, narrator performance rating, progress meter, reflection journal,
    audio preview player, and complete update modal.
    """
    entry = get_object_or_404(AudiobookEntry, id=audiobook_id, user=request.user)
    context = {
        "audiobook": entry,
        "status_choices": AudiobookStatus.choices,
    }
    return render(request, "audiobooks/detail.html", context)

@login_required
def update_audiobook_details_view(request, audiobook_id):
    """
    Handles updates to audiobook tracking details, ratings, narrator review,
    insights, dates, and audio duration.
    """
    entry = get_object_or_404(AudiobookEntry, id=audiobook_id, user=request.user)

    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in AudiobookStatus.values:
            entry.status = new_status
            if new_status == AudiobookStatus.COMPLETED and not entry.finish_date:
                entry.finish_date = timezone.now().date()
                if entry.duration_minutes > 0:
                    entry.current_progress_minutes = entry.duration_minutes
            elif new_status == AudiobookStatus.LISTENING and not entry.start_date:
                entry.start_date = timezone.now().date()

        # Ratings
        rating_input = request.POST.get("rating")
        entry.rating = float(rating_input) if rating_input else None

        narrator_rating_input = request.POST.get("narrator_rating")
        entry.narrator_rating = float(narrator_rating_input) if narrator_rating_input else None

        # Playback speed
        speed_input = request.POST.get("playback_speed")
        if speed_input:
            try:
                entry.playback_speed = float(speed_input)
            except ValueError:
                pass

        # Duration & Progress
        duration_input = request.POST.get("duration_minutes")
        if duration_input is not None:
            entry.duration_minutes = max(int(duration_input or 0), 0)

        progress_input = request.POST.get("current_progress_minutes")
        if progress_input is not None:
            entry.current_progress_minutes = max(int(progress_input or 0), 0)
            if entry.duration_minutes > 0 and entry.current_progress_minutes >= entry.duration_minutes:
                entry.status = AudiobookStatus.COMPLETED
                if not entry.finish_date:
                    entry.finish_date = timezone.now().date()

        # Dates
        start_date_input = request.POST.get("start_date")
        if start_date_input:
            try:
                entry.start_date = timezone.datetime.strptime(start_date_input, "%Y-%m-%d").date()
            except ValueError:
                pass
        elif request.POST.get("clear_start_date") == "1":
            entry.start_date = None

        finish_date_input = request.POST.get("finish_date")
        if finish_date_input:
            try:
                entry.finish_date = timezone.datetime.strptime(finish_date_input, "%Y-%m-%d").date()
            except ValueError:
                pass
        elif request.POST.get("clear_finish_date") == "1":
            entry.finish_date = None

        # Reflections
        entry.review = request.POST.get("review", "").strip()
        entry.mind_changing_takeaways = request.POST.get("mind_changing_takeaways", "").strip()
        entry.favorite_quotes = request.POST.get("favorite_quotes", "").strip()
        
        relive_count_input = request.POST.get("relive_count")
        if relive_count_input is not None:
            entry.relive_count = max(int(relive_count_input or 0), 0)

        # Custom Cover file upload
        if "cover_file" in request.FILES:
            entry.custom_cover = request.FILES["cover_file"]

        # Custom metadata adjustments if manual
        if entry.is_custom:
            entry.title = request.POST.get("title", entry.title).strip() or entry.title
            entry.author = request.POST.get("author", entry.author).strip()
            entry.narrator = request.POST.get("narrator", entry.narrator).strip() or "Narrator Unlisted"
            entry.genre = request.POST.get("genre", entry.genre).strip()

        entry.save()
        messages.success(request, f"Updated audiobook notes for '{entry.title}'.")
        return redirect("audiobook_detail", audiobook_id=entry.id)

    return redirect("audiobook_detail", audiobook_id=entry.id)

@login_required
def update_audiobook_progress_view(request, audiobook_id):
    """
    Quick stepper endpoint to update minutes listened from list or detail cards.
    """
    entry = get_object_or_404(AudiobookEntry, id=audiobook_id, user=request.user)

    if request.method == "POST":
        step = request.POST.get("step") # e.g. +15, +30, -15
        progress_val = request.POST.get("progress_minutes")

        if step:
            try:
                entry.current_progress_minutes = max(entry.current_progress_minutes + int(step), 0)
            except ValueError:
                pass
        elif progress_val is not None:
            try:
                entry.current_progress_minutes = max(int(progress_val), 0)
            except ValueError:
                pass

        # Auto-complete check
        if entry.duration_minutes > 0 and entry.current_progress_minutes >= entry.duration_minutes:
            entry.status = AudiobookStatus.COMPLETED
            if not entry.finish_date:
                entry.finish_date = timezone.now().date()
        elif entry.status == AudiobookStatus.PLAN_TO_LISTEN and entry.current_progress_minutes > 0:
            entry.status = AudiobookStatus.LISTENING
            if not entry.start_date:
                entry.start_date = timezone.now().date()

        # Handle direct status change from card buttons
        new_status = request.POST.get("status")
        if new_status in AudiobookStatus.values:
            entry.status = new_status
            if new_status == AudiobookStatus.COMPLETED:
                if not entry.finish_date:
                    entry.finish_date = timezone.now().date()
                if entry.duration_minutes > 0:
                    entry.current_progress_minutes = entry.duration_minutes
            elif new_status == AudiobookStatus.LISTENING and not entry.start_date:
                entry.start_date = timezone.now().date()

        entry.save()
        messages.success(request, f"Listening progress updated for '{entry.title}'.")

    next_url = request.META.get("HTTP_REFERER") or "audiobook_list"
    return redirect(next_url)

@login_required
def delete_audiobook_view(request, audiobook_id):
    """
    Removes an audiobook entry completely.
    """
    entry = get_object_or_404(AudiobookEntry, id=audiobook_id, user=request.user)
    if request.method == "POST":
        title = entry.title
        entry.delete()
        messages.success(request, f"Removed '{title}' from your Audiobook Chronicle.")
        return redirect("audiobook_list")

    return redirect("audiobook_detail", audiobook_id=audiobook_id)
