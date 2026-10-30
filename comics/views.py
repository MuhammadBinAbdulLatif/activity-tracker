import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.utils import timezone
from .models import ComicMangaEntry, ComicMangaType, ComicMangaStatus
from services.comic_manga_service import ComicMangaService

@login_required
def comic_list_view(request):
    """
    Renders the dedicated Comics & Manga section categorized by Currently Reading,
    Plan to Read watchlist, and Completed / Library, with item type filters.
    """
    type_filter = request.GET.get("type", "ALL").upper()
    entries = ComicMangaEntry.objects.filter(user=request.user)

    if type_filter in [ComicMangaType.COMIC, ComicMangaType.MANGA, ComicMangaType.LIGHT_NOVEL]:
        entries = entries.filter(item_type=type_filter)

    reading = entries.filter(status=ComicMangaStatus.READING)
    wishlist = entries.filter(status=ComicMangaStatus.PLAN_TO_READ)
    completed = entries.filter(status=ComicMangaStatus.COMPLETED)
    on_hold = entries.filter(status=ComicMangaStatus.ON_HOLD)
    dropped = entries.filter(status=ComicMangaStatus.DROPPED)

    context = {
        "reading": reading,
        "wishlist": wishlist,
        "completed": completed,
        "on_hold": on_hold,
        "dropped": dropped,
        "total_count": entries.count(),
        "type_filter": type_filter,
        "type_choices": ComicMangaType.choices,
        "status_choices": ComicMangaStatus.choices,
    }
    return render(request, "comics/list.html", context)

@login_required
def search_comics_view(request):
    """
    Live HTMX or JSON search for Comics & Manga via Comic Vine and AniList APIs.
    Excludes DROPPED and deleted items from is_tracked.
    """
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "ALL").upper()

    if not query:
        return render(request, "comics/partials/search_results.html", {"results": []})

    results = ComicMangaService.search_all(query, category_filter=category, limit=12)

    # Exclude DROPPED from active tracked items
    tracked_external_ids = set(
        ComicMangaEntry.objects.filter(user=request.user, external_id__gt="")
        .exclude(status=ComicMangaStatus.DROPPED)
        .values_list("external_id", flat=True)
    )

    formatted_results = []
    for item in results:
        ext_id = item.get("external_id", "")
        formatted_results.append({
            "external_id": ext_id,
            "title": item.get("title"),
            "original_title": item.get("original_title") or "",
            "item_type": item.get("item_type") or "MANGA",
            "creator_author": item.get("creator_author") or "",
            "artist": item.get("artist") or "",
            "publisher": item.get("publisher") or "",
            "start_year": item.get("start_year") or "",
            "total_chapters": item.get("total_chapters") or 0,
            "total_volumes": item.get("total_volumes") or 0,
            "cover_url": item.get("cover_url") or "",
            "description": item.get("description") or "",
            "source": item.get("source") or "",
            "is_tracked": ext_id in tracked_external_ids if ext_id else False,
        })

    if request.headers.get("HX-Request"):
        return render(request, "comics/partials/search_results.html", {"results": formatted_results})
    return JsonResponse({"results": formatted_results})

@login_required
def add_comic_view(request):
    """
    Tracks a comic or manga from search or via custom manual entry.
    """
    if request.method == "POST":
        external_id = request.POST.get("external_id", "").strip()
        title = request.POST.get("title", "").strip()
        original_title = request.POST.get("original_title", "").strip()
        item_type = request.POST.get("item_type", ComicMangaType.MANGA)
        creator_author = request.POST.get("creator_author", "").strip()
        artist = request.POST.get("artist", "").strip()
        publisher = request.POST.get("publisher", "").strip()
        cover_url = request.POST.get("cover_url", "").strip()
        description = request.POST.get("description", "").strip()
        status = request.POST.get("status", ComicMangaStatus.PLAN_TO_READ)

        start_year = request.POST.get("start_year")
        total_chapters = request.POST.get("total_chapters")
        total_volumes = request.POST.get("total_volumes")
        current_chapter = request.POST.get("current_chapter", 0)
        current_volume = request.POST.get("current_volume", 0)

        try:
            start_year = int(start_year) if start_year else None
        except (ValueError, TypeError):
            start_year = None

        try:
            total_chapters = int(total_chapters) if total_chapters else 0
        except (ValueError, TypeError):
            total_chapters = 0

        try:
            total_volumes = int(total_volumes) if total_volumes else 0
        except (ValueError, TypeError):
            total_volumes = 0

        try:
            current_chapter = int(current_chapter) if current_chapter else 0
        except (ValueError, TypeError):
            current_chapter = 0

        try:
            current_volume = int(current_volume) if current_volume else 0
        except (ValueError, TypeError):
            current_volume = 0

        # Handle custom cover upload
        custom_cover = request.FILES.get("custom_cover")

        if not title:
            messages.error(request, "Title is required to track a comic or manga.")
            return redirect("comic_list")

        # Check if already tracked
        if external_id:
            existing = ComicMangaEntry.objects.filter(user=request.user, external_id=external_id).first()
            if existing:
                if existing.status == ComicMangaStatus.DROPPED:
                    existing.status = status
                    existing.save()
                    messages.success(request, f"Re-activated '{existing.title}' in your library.")
                    return redirect("comic_detail", id=existing.id)
                else:
                    messages.info(request, f"'{existing.title}' is already in your tracking library.")
                    return redirect("comic_detail", id=existing.id)

        # Set default start date if starting right now
        start_date = timezone.now().date() if status == ComicMangaStatus.READING else None

        entry = ComicMangaEntry.objects.create(
            user=request.user,
            external_id=external_id,
            item_type=item_type,
            title=title,
            original_title=original_title,
            creator_author=creator_author,
            artist=artist,
            publisher=publisher,
            start_year=start_year,
            total_chapters=total_chapters,
            total_volumes=total_volumes,
            current_chapter=current_chapter,
            current_volume=current_volume,
            cover_url=cover_url,
            custom_cover=custom_cover,
            description=description,
            status=status,
            start_date=start_date
        )

        messages.success(request, f"Added '{entry.title}' to your {entry.get_status_display().lower()}!")
        return redirect("comic_detail", id=entry.id)

    return redirect("comic_list")

@login_required
def comic_detail_view(request, id):
    """
    Renders deep detail hub for a specific comic or manga entry.
    """
    entry = get_object_or_404(ComicMangaEntry, id=id, user=request.user)
    context = {
        "entry": entry,
        "type_choices": ComicMangaType.choices,
        "status_choices": ComicMangaStatus.choices,
    }
    return render(request, "comics/detail.html", context)

@login_required
def update_comic_progress_view(request, id):
    """
    Updates reading progress (chapter or volume) and auto-completes if threshold reached.
    """
    entry = get_object_or_404(ComicMangaEntry, id=id, user=request.user)
    if request.method == "POST":
        delta_chapter = request.POST.get("delta_chapter")
        delta_volume = request.POST.get("delta_volume")
        set_chapter = request.POST.get("current_chapter")
        set_volume = request.POST.get("current_volume")

        if delta_chapter is not None:
            try:
                new_chap = entry.current_chapter + int(delta_chapter)
                if entry.total_chapters > 0:
                    new_chap = min(entry.total_chapters, new_chap)
                entry.current_chapter = max(0, new_chap)
            except ValueError:
                pass
        elif set_chapter is not None:
            try:
                new_chap = int(set_chapter)
                if entry.total_chapters > 0:
                    new_chap = min(entry.total_chapters, new_chap)
                entry.current_chapter = max(0, new_chap)
            except ValueError:
                pass

        if delta_volume is not None:
            try:
                new_vol = entry.current_volume + int(delta_volume)
                if entry.total_volumes > 0:
                    new_vol = min(entry.total_volumes, new_vol)
                entry.current_volume = max(0, new_vol)
            except ValueError:
                pass
        elif set_volume is not None:
            try:
                new_vol = int(set_volume)
                if entry.total_volumes > 0:
                    new_vol = min(entry.total_volumes, new_vol)
                entry.current_volume = max(0, new_vol)
            except ValueError:
                pass

        # If it was planned to read, switch to reading
        if entry.status == ComicMangaStatus.PLAN_TO_READ and (entry.current_chapter > 0 or entry.current_volume > 0):
            entry.status = ComicMangaStatus.READING
            if not entry.start_date:
                entry.start_date = timezone.now().date()

        # Check for auto-completion:
        # If total volumes reached, auto-complete chapters to total chapters as well
        if entry.total_volumes > 0 and entry.current_volume >= entry.total_volumes:
            if entry.total_chapters > 0:
                entry.current_chapter = entry.total_chapters
            entry.status = ComicMangaStatus.COMPLETED
            if not entry.finish_date:
                entry.finish_date = timezone.now().date()
        elif entry.total_chapters > 0 and entry.current_chapter >= entry.total_chapters:
            if entry.total_volumes > 0:
                entry.current_volume = entry.total_volumes
            entry.status = ComicMangaStatus.COMPLETED
            if not entry.finish_date:
                entry.finish_date = timezone.now().date()

        entry.save()

        next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or redirect("comic_detail", id=entry.id).url
        return redirect(next_url)

    return redirect("comic_detail", id=entry.id)

@login_required
def update_comic_details_view(request, id):
    """
    Comprehensive updates to comic/manga metadata, ratings, dates, notes.
    """
    entry = get_object_or_404(ComicMangaEntry, id=id, user=request.user)
    if request.method == "POST":
        entry.title = request.POST.get("title", entry.title).strip()
        entry.original_title = request.POST.get("original_title", entry.original_title).strip()
        entry.item_type = request.POST.get("item_type", entry.item_type)
        entry.creator_author = request.POST.get("creator_author", entry.creator_author).strip()
        entry.artist = request.POST.get("artist", entry.artist).strip()
        entry.publisher = request.POST.get("publisher", entry.publisher).strip()
        entry.status = request.POST.get("status", entry.status)

        # Numbers
        start_year = request.POST.get("start_year")
        total_chapters = request.POST.get("total_chapters")
        total_volumes = request.POST.get("total_volumes")
        current_chapter = request.POST.get("current_chapter")
        current_volume = request.POST.get("current_volume")

        try:
            entry.start_year = int(start_year) if start_year else None
        except (ValueError, TypeError):
            pass

        try:
            entry.total_chapters = int(total_chapters) if total_chapters else 0
        except (ValueError, TypeError):
            pass

        try:
            entry.total_volumes = int(total_volumes) if total_volumes else 0
        except (ValueError, TypeError):
            pass

        try:
            entry.current_chapter = int(current_chapter) if current_chapter else 0
        except (ValueError, TypeError):
            pass

        try:
            entry.current_volume = int(current_volume) if current_volume else 0
        except (ValueError, TypeError):
            pass

        # Ratings
        rating = request.POST.get("rating")
        art_rating = request.POST.get("art_rating")

        try:
            entry.rating = float(rating) if rating else None
        except (ValueError, TypeError):
            entry.rating = None

        try:
            entry.art_rating = float(art_rating) if art_rating else None
        except (ValueError, TypeError):
            entry.art_rating = None

        # Dates
        start_date = request.POST.get("start_date")
        finish_date = request.POST.get("finish_date")

        entry.start_date = start_date if start_date else None
        entry.finish_date = finish_date if finish_date else None

        # Highlights & Reviews
        entry.favorite_arc_or_issue = request.POST.get("favorite_arc_or_issue", "").strip()
        entry.review = request.POST.get("review", "").strip()
        entry.notes = request.POST.get("notes", "").strip()

        # Custom Cover
        if "custom_cover" in request.FILES:
            entry.custom_cover = request.FILES["custom_cover"]

        cover_url = request.POST.get("cover_url", "").strip()
        if cover_url:
            entry.cover_url = cover_url

        entry.save()
        messages.success(request, f"Updated details for '{entry.title}'.")

    return redirect("comic_detail", id=entry.id)

@login_required
def delete_comic_view(request, id):
    """
    Deletes a comic or manga entry from the user's library.
    """
    entry = get_object_or_404(ComicMangaEntry, id=id, user=request.user)
    if request.method == "POST":
        title = entry.title
        entry.delete()
        messages.success(request, f"Removed '{title}' from your library.")
        return redirect("comic_list")
    return redirect("comic_detail", id=entry.id)
