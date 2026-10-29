import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.utils import timezone
from .models import MovieEntry, MovieStatus
from services.tmdb import tmdb_service

@login_required
def movie_list_view(request):
    """
    Renders the dedicated Movies section categorized by Currently Watching,
    Watchlist (Plan to Watch), and Completed / Watched History.
    """
    entries = MovieEntry.objects.filter(user=request.user)
    
    watching = entries.filter(status=MovieStatus.WATCHING)
    watchlist = entries.filter(status=MovieStatus.PLAN_TO_WATCH)
    completed = entries.filter(status=MovieStatus.COMPLETED)
    dropped = entries.filter(status=MovieStatus.DROPPED)

    context = {
        "watching": watching,
        "watchlist": watchlist,
        "completed": completed,
        "dropped": dropped,
        "total_count": entries.count(),
    }
    return render(request, "movies/list.html", context)

@login_required
def search_movies_view(request):
    """
    Live HTMX or JSON search for movies via TMDB.
    """
    query = request.GET.get("q", "").strip()
    if not query:
        return render(request, "movies/partials/search_results.html", {"results": []})

    data = tmdb_service.search_movies(query)
    results = data.get("results", [])[:8] # Top 8 results
    
    # Check if user already tracks these items
    tracked_tmdb_ids = set(
        MovieEntry.objects.filter(user=request.user, tmdb_id__isnull=False)
        .values_list("tmdb_id", flat=True)
    )

    formatted_results = []
    for item in results:
        t_id = item.get("id")
        formatted_results.append({
            "tmdb_id": t_id,
            "title": item.get("title"),
            "release_date": item.get("release_date") or "",
            "release_year": item.get("release_date", "")[:4] if item.get("release_date") else "",
            "overview": item.get("overview", ""),
            "poster_path": item.get("poster_path") or "",
            "poster_url": f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}" if item.get("poster_path") else "https://images.unsplash.com/photo-1485846234645-a62644f84728?auto=format&fit=crop&w=400&q=80",
            "vote_average": item.get("vote_average", 0),
            "is_tracked": t_id in tracked_tmdb_ids,
        })

    if request.headers.get("HX-Request"):
        return render(request, "movies/partials/search_results.html", {"results": formatted_results})
    return JsonResponse({"results": formatted_results})

@login_required
def add_movie_view(request):
    """
    Tracks a movie from TMDB or via manual entry.
    """
    if request.method == "POST":
        tmdb_id = request.POST.get("tmdb_id")
        status = request.POST.get("status", MovieStatus.PLAN_TO_WATCH)
        rating = request.POST.get("rating") or None
        review = request.POST.get("review", "").strip()

        if tmdb_id:
            details = tmdb_service.get_movie_details(tmdb_id)
            if details:
                genres = ", ".join([g["name"] for g in details.get("genres", [])])
                credits = details.get("credits", {})
                directors = [c["name"] for c in credits.get("crew", []) if c.get("job") == "Director"]
                director = ", ".join(directors[:2])
                cast_names = [c["name"] for c in credits.get("cast", [])[:10]]
                cast_str = ", ".join(cast_names)

                entry, created = MovieEntry.objects.update_or_create(
                    user=request.user,
                    tmdb_id=details.get("id"),
                    defaults={
                        "title": details.get("title") or "Untitled",
                        "original_title": details.get("original_title", ""),
                        "release_date": details.get("release_date") or None,
                        "runtime": details.get("runtime") or 0,
                        "poster_path": details.get("poster_path", ""),
                        "backdrop_path": details.get("backdrop_path", ""),
                        "tagline": details.get("tagline", ""),
                        "overview": details.get("overview", ""),
                        "genres": genres,
                        "director": director,
                        "cast": cast_str,
                        "status": status,
                        "rating": float(rating) if rating else None,
                        "review": review,
                        "watch_date": timezone.now().date() if status == MovieStatus.COMPLETED else None,
                    }
                )
                action = "Added" if created else "Updated"
                messages.success(request, f"{action} '{entry.title}' to your {entry.get_status_display()}.")
                return redirect("movie_detail", movie_id=entry.id)
        
        # Manual Fallback Entry
        title = request.POST.get("title", "").strip()
        if title:
            custom_poster = request.FILES.get("poster_file")
            watch_date_input = request.POST.get("watch_date")
            watch_date = None
            if watch_date_input:
                try:
                    watch_date = timezone.datetime.strptime(watch_date_input, "%Y-%m-%d").date()
                except ValueError:
                    watch_date = None
            elif status == MovieStatus.COMPLETED:
                watch_date = timezone.now().date()

            entry = MovieEntry.objects.create(
                user=request.user,
                title=title,
                release_date=request.POST.get("release_date") or None,
                runtime=int(request.POST.get("runtime") or 0),
                overview=request.POST.get("overview", "").strip(),
                director=request.POST.get("director", "").strip(),
                cast=request.POST.get("cast", "").strip(),
                genres=request.POST.get("genres", "").strip(),
                status=status,
                rating=float(rating) if rating else None,
                review=review,
                is_custom=True,
                watch_date=watch_date,
                custom_poster=custom_poster,
            )
            messages.success(request, f"Created custom movie entry '{entry.title}'.")
            return redirect("movie_detail", movie_id=entry.id)

    return redirect("movie_list")

@login_required
def movie_detail_view(request, movie_id):
    """
    Dedicated view for a single movie: provides full synopsis, cast,
    director, status switching / reversion, personal rating, review, and rewatch count.
    """
    movie = get_object_or_404(MovieEntry, id=movie_id, user=request.user)

    # If cast is empty but tmdb_id exists, backfill cast & backdrop from TMDB
    if not movie.cast and movie.tmdb_id:
        details = tmdb_service.get_movie_details(movie.tmdb_id)
        if details:
            credits = details.get("credits", {})
            cast_names = [c["name"] for c in credits.get("cast", [])[:10]]
            if cast_names:
                movie.cast = ", ".join(cast_names)
            if not movie.tagline:
                movie.tagline = details.get("tagline", "")
            if not movie.backdrop_path:
                movie.backdrop_path = details.get("backdrop_path", "")
            movie.save()

    context = {
        "movie": movie,
        "status_choices": MovieStatus.choices,
    }
    return render(request, "movies/detail.html", context)

@login_required
def update_movie_details_view(request, movie_id):
    """
    Handles updates to a movie's status, personal rating, review, watch date, and rewatch count.
    Supports complete status reversion (e.g. Completed -> Plan to Watch).
    """
    movie = get_object_or_404(MovieEntry, id=movie_id, user=request.user)

    if request.method == "POST":
        new_status = request.POST.get("status")
        rating_input = request.POST.get("rating")
        review_input = request.POST.get("review", "")
        rewatch_input = request.POST.get("rewatch_count")
        watch_date_input = request.POST.get("watch_date")

        # Update status & manage watch date
        if new_status in [s[0] for s in MovieStatus.choices]:
            old_status = movie.status
            movie.status = new_status
            
            # If changing to completed and no date set, default to today
            if new_status == MovieStatus.COMPLETED and not watch_date_input and not movie.watch_date:
                movie.watch_date = timezone.now().date()
            # If reverting out of completed to plan_to_watch, allow clearing date
            elif new_status == MovieStatus.PLAN_TO_WATCH and not watch_date_input:
                movie.watch_date = None

        if watch_date_input:
            try:
                movie.watch_date = timezone.datetime.strptime(watch_date_input, "%Y-%m-%d").date()
            except ValueError:
                pass
        elif request.POST.get("clear_watch_date") == "1":
            movie.watch_date = None

        # Rating
        if rating_input:
            try:
                movie.rating = float(rating_input)
            except ValueError:
                pass
        elif rating_input == "":
            movie.rating = None

        # Review & Rewatch
        movie.review = review_input.strip()
        if rewatch_input:
            try:
                movie.rewatch_count = max(0, int(rewatch_input))
            except ValueError:
                pass

        # If custom movie, allow editing metadata
        if movie.is_custom:
            if "title" in request.POST and request.POST["title"].strip():
                movie.title = request.POST["title"].strip()
            if "director" in request.POST:
                movie.director = request.POST["director"].strip()
            if "cast" in request.POST:
                movie.cast = request.POST["cast"].strip()
            if "overview" in request.POST:
                movie.overview = request.POST["overview"].strip()
            if "runtime" in request.POST and request.POST["runtime"].isdigit():
                movie.runtime = int(request.POST["runtime"])
            if "poster_file" in request.FILES:
                movie.custom_poster = request.FILES["poster_file"]

        movie.save()
        messages.success(request, f"Updated '{movie.title}' successfully.")
        return redirect("movie_detail", movie_id=movie.id)

    return redirect("movie_detail", movie_id=movie.id)

@login_required
def update_movie_status_view(request, movie_id):
    """
    Quick status toggle from the list view.
    """
    entry = get_object_or_404(MovieEntry, id=movie_id, user=request.user)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in [s[0] for s in MovieStatus.choices]:
            entry.status = new_status
            if new_status == MovieStatus.COMPLETED and not entry.watch_date:
                entry.watch_date = timezone.now().date()
            entry.save()
            messages.success(request, f"Moved '{entry.title}' to {entry.get_status_display()}.")

    return redirect("movie_list")

@login_required
def rewatch_movie_view(request, movie_id):
    """
    Increments the rewatch counter and logs today as watch date.
    """
    entry = get_object_or_404(MovieEntry, id=movie_id, user=request.user)
    entry.rewatch_count += 1
    entry.watch_date = timezone.now().date()
    entry.status = MovieStatus.COMPLETED
    entry.save()
    messages.success(request, f"Logged rewatch for '{entry.title}' (Total rewatches: {entry.rewatch_count}).")
    return redirect("movie_detail", movie_id=entry.id)

@login_required
def delete_movie_view(request, movie_id):
    """
    Deletes a movie from the user's tracker.
    """
    entry = get_object_or_404(MovieEntry, id=movie_id, user=request.user)
    if request.method == "POST":
        title = entry.title
        entry.delete()
        messages.success(request, f"Removed '{title}' from your tracker.")
        return redirect("movie_list")
    return redirect("movie_detail", movie_id=entry.id)
