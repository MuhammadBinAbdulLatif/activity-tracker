from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.utils import timezone
from .models import SeriesEntry, SeasonEntry, SeriesUserStatus, SeriesShowStatus
from .engine import SeriesProgressionEngine
from services.tmdb import tmdb_service

@login_required
def series_list_view(request):
    """
    Renders the dedicated Series section categorized by Currently Watching,
    Waiting for Next Season, Watchlist, and Completed.
    """
    entries = SeriesEntry.objects.filter(user=request.user)
    
    watching = entries.filter(user_status=SeriesUserStatus.WATCHING)
    waiting = entries.filter(user_status=SeriesUserStatus.WAITING_FOR_NEXT_SEASON)
    watchlist = entries.filter(user_status=SeriesUserStatus.PLAN_TO_WATCH)
    completed = entries.filter(user_status=SeriesUserStatus.COMPLETED)
    dropped = entries.filter(user_status=SeriesUserStatus.DROPPED)

    context = {
        "watching": watching,
        "waiting": waiting,
        "watchlist": watchlist,
        "completed": completed,
        "dropped": dropped,
        "total_count": entries.count(),
    }
    return render(request, "series/list.html", context)

@login_required
def search_series_view(request):
    """
    Live HTMX or JSON search for TV shows via TMDB.
    """
    query = request.GET.get("q", "").strip()
    if not query:
        return render(request, "series/partials/search_results.html", {"results": []})

    data = tmdb_service.search_series(query)
    results = data.get("results", [])[:8]

    tracked_tmdb_ids = set(
        SeriesEntry.objects.filter(user=request.user, tmdb_id__isnull=False)
        .values_list("tmdb_id", flat=True)
    )

    formatted_results = []
    for item in results:
        t_id = item.get("id")
        formatted_results.append({
            "tmdb_id": t_id,
            "title": item.get("name"),
            "first_air_date": item.get("first_air_date") or "",
            "release_year": item.get("first_air_date", "")[:4] if item.get("first_air_date") else "",
            "overview": item.get("overview", ""),
            "poster_path": item.get("poster_path") or "",
            "poster_url": f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}" if item.get("poster_path") else "https://images.unsplash.com/photo-1578632767115-351597cf2477?auto=format&fit=crop&w=400&q=80",
            "vote_average": item.get("vote_average", 0),
            "is_tracked": t_id in tracked_tmdb_ids,
        })

    if request.headers.get("HX-Request"):
        return render(request, "series/partials/search_results.html", {"results": formatted_results})
    return JsonResponse({"results": formatted_results})

@login_required
def add_series_view(request):
    """
    Tracks a TV series from TMDB or via manual entry.
    """
    if request.method == "POST":
        tmdb_id = request.POST.get("tmdb_id")
        status = request.POST.get("status", SeriesUserStatus.WATCHING)

        if tmdb_id:
            details = tmdb_service.get_series_details(tmdb_id)
            if details:
                genres = ", ".join([g["name"] for g in details.get("genres", [])])
                show_status = details.get("status", SeriesShowStatus.RETURNING)

                entry, created = SeriesEntry.objects.update_or_create(
                    user=request.user,
                    tmdb_id=details.get("id"),
                    defaults={
                        "title": details.get("name") or "Untitled",
                        "first_air_date": details.get("first_air_date") or None,
                        "poster_path": details.get("poster_path", ""),
                        "backdrop_path": details.get("backdrop_path", ""),
                        "overview": details.get("overview", ""),
                        "genres": genres,
                        "show_status": show_status,
                        "total_seasons": details.get("number_of_seasons", 1),
                        "total_episodes": details.get("number_of_episodes", 0),
                        "user_status": status,
                        "current_season_number": 1,
                        "current_episode_number": 0,
                    }
                )

                # Sync seasons and episode airing info
                SeriesProgressionEngine.sync_tmdb_metadata(entry)

                messages.success(request, f"Tracking '{entry.title}'.")
                return redirect("series_list")

        # Manual Fallback
        title = request.POST.get("title", "").strip()
        if title:
            custom_poster = request.FILES.get("poster_file")
            total_seasons = int(request.POST.get("total_seasons") or 1)
            total_episodes = int(request.POST.get("total_episodes") or 10)
            current_season = int(request.POST.get("current_season_number") or 1)
            current_episode = int(request.POST.get("current_episode_number") or 0)
            rating = request.POST.get("rating") or None
            review = request.POST.get("review", "").strip()

            entry = SeriesEntry.objects.create(
                user=request.user,
                title=title,
                first_air_date=request.POST.get("first_air_date") or None,
                overview=request.POST.get("overview", "").strip(),
                genres=request.POST.get("genres", "").strip(),
                total_seasons=total_seasons,
                total_episodes=total_episodes,
                current_season_number=current_season,
                current_episode_number=current_episode,
                user_status=status,
                rating=float(rating) if rating else None,
                review=review,
                is_custom=True,
                custom_poster=custom_poster,
            )
            # Create season entries up to total_seasons
            for s_num in range(1, total_seasons + 1):
                ep_count = total_episodes // total_seasons if total_seasons > 0 else 10
                is_comp = (status == SeriesUserStatus.COMPLETED) or (s_num < current_season)
                SeasonEntry.objects.create(
                    series=entry,
                    season_number=s_num,
                    episode_count=ep_count,
                    name=f"Season {s_num}",
                    is_completed=is_comp,
                    completed_at=timezone.now() if is_comp else None
                )
            messages.success(request, f"Created custom series '{entry.title}'.")
            return redirect("series_list")

    return redirect("series_list")

@login_required
def advance_episode_view(request, series_id):
    """
    HTMX or POST action: marks the next episode watched (+1 Ep),
    checks for season completion and automatic next-season progression.
    """
    entry = get_object_or_404(SeriesEntry, id=series_id, user=request.user)
    result = SeriesProgressionEngine.advance_episode(entry)

    if request.headers.get("HX-Request"):
        return render(request, "series/partials/series_card_inner.html", {"series": entry, "toast": result})

    messages.add_message(request, messages.SUCCESS if result["toast_type"] == "success" else messages.INFO, result["message"])
    return redirect("series_list")

@login_required
def sync_series_metadata_view(request, series_id):
    """
    Manual trigger to pull freshest broadcast info and air dates from TMDB.
    """
    entry = get_object_or_404(SeriesEntry, id=series_id, user=request.user)
    SeriesProgressionEngine.sync_tmdb_metadata(entry)
    messages.success(request, f"Synced broadcast schedule for '{entry.title}'.")
    return redirect("series_list")
