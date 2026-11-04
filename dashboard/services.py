"""
Service for aggregating real user chronicle data across all media and activity models:
- Movies (MovieEntry)
- Series (SeriesEntry, EpisodeLog)
- Books (BookEntry)
- Audiobooks (AudiobookEntry)
- Comics & Manga (ComicMangaEntry)
- Video Games (GameEntry)
- Board Games (BoardGameEntry)
- Exercises & Habits (UserExerciseTrack, ExerciseLog)
"""

from datetime import datetime, timedelta, date
from django.utils import timezone
from collections import defaultdict
from decimal import Decimal

from movies.models import MovieEntry, MovieStatus
from series.models import SeriesEntry, SeriesUserStatus, EpisodeLog
from books.models import BookEntry, BookStatus
from audiobooks.models import AudiobookEntry, AudiobookStatus
from comics.models import ComicMangaEntry, ComicMangaStatus
from games.models import GameEntry, GameStatus
from boardgames.models import BoardGameEntry, BoardGameStatus
from exercises.models import UserExerciseTrack, ExerciseTrackingStatus, ExerciseLog


def _make_stars(rating, max_rating=5):
    """Convert a rating out of 5 or 10 into star string like ★★★★½ or ★★★★☆."""
    if not rating:
        return ""
    r = float(rating)
    if r > 5.0:
        r = r / 2.0  # normalize 10-point scale to 5 stars
    r = min(5.0, max(0.0, r))
    full = int(r)
    half = 1 if (r - full) >= 0.4 else 0
    empty = 5 - full - half
    return "★" * full + ("½" if half else "") + "☆" * empty


def get_real_dashboard_data(user):
    today = timezone.localdate()
    current_year = today.year
    first_of_month = today.replace(day=1)

    # -------------------------------------------------------------------------
    # 1. Fetch user data across all categories
    # -------------------------------------------------------------------------
    user_movies = MovieEntry.objects.filter(user=user)
    user_series = SeriesEntry.objects.filter(user=user)
    user_episode_logs = EpisodeLog.objects.filter(series__user=user).select_related("series")
    user_books = BookEntry.objects.filter(user=user)
    user_audiobooks = AudiobookEntry.objects.filter(user=user)
    user_comics = ComicMangaEntry.objects.filter(user=user)
    user_games = GameEntry.objects.filter(user=user)
    user_boardgames = BoardGameEntry.objects.filter(user=user)
    user_tracks = UserExerciseTrack.objects.filter(user=user).select_related("exercise")
    user_exercise_logs = ExerciseLog.objects.filter(user=user).select_related("exercise")

    # -------------------------------------------------------------------------
    # 2. Activity Dates Aggregation (for Heatmap and Streak)
    # -------------------------------------------------------------------------
    daily_activity_map = defaultdict(lambda: {"count": 0, "items": []})

    # Movies
    for m in user_movies:
        d = m.watch_date or (m.updated_at.date() if m.status == MovieStatus.COMPLETED else None)
        if d:
            daily_activity_map[d]["count"] += 1
            daily_activity_map[d]["items"].append(f"Movie: {m.title}")

    # Series Episode Logs
    for ep in user_episode_logs:
        d = ep.watched_at.date() if ep.watched_at else None
        if d:
            daily_activity_map[d]["count"] += 1
            daily_activity_map[d]["items"].append(f"Episode: {ep.series.title} S{ep.season_number}E{ep.episode_number}")

    # Books
    for b in user_books:
        d = b.finish_date or (b.updated_at.date() if b.status == BookStatus.COMPLETED else None)
        if d:
            daily_activity_map[d]["count"] += 1
            daily_activity_map[d]["items"].append(f"Book: {b.title}")

    # Audiobooks
    for ab in user_audiobooks:
        d = ab.finish_date or (ab.updated_at.date() if ab.status == AudiobookStatus.COMPLETED else None)
        if d:
            daily_activity_map[d]["count"] += 1
            daily_activity_map[d]["items"].append(f"Audiobook: {ab.title}")

    # Comics
    for c in user_comics:
        d = c.finish_date or (c.updated_at.date() if c.status == ComicMangaStatus.COMPLETED else None)
        if d:
            daily_activity_map[d]["count"] += 1
            daily_activity_map[d]["items"].append(f"Comic: {c.title}")

    # Games
    for g in user_games:
        d = g.finish_date or (g.updated_at.date() if g.status == GameStatus.COMPLETED else None)
        if d:
            daily_activity_map[d]["count"] += 1
            daily_activity_map[d]["items"].append(f"Game: {g.title}")

    # Board games
    for bg in user_boardgames:
        d = bg.last_played
        if d:
            daily_activity_map[d]["count"] += 1
            daily_activity_map[d]["items"].append(f"Board Game: {bg.title}")

    # Exercise logs
    for ex in user_exercise_logs:
        d = ex.logged_date
        if d:
            daily_activity_map[d]["count"] += 1
            daily_activity_map[d]["items"].append(f"Exercise: {ex.exercise.name}")

    # -------------------------------------------------------------------------
    # 3. Active Streak Calculation
    # -------------------------------------------------------------------------
    streak = 0
    # Streak can start today if active today, or yesterday if already logged yesterday
    check_day = today if today in daily_activity_map else (today - timedelta(days=1))
    while check_day in daily_activity_map:
        streak += 1
        check_day -= timedelta(days=1)

    # -------------------------------------------------------------------------
    # 4. Total Items Completed This Year & Hours Consumed This Month
    # -------------------------------------------------------------------------
    completed_movies_year = user_movies.filter(status=MovieStatus.COMPLETED, watch_date__year=current_year).count()
    completed_series_year = user_series.filter(user_status=SeriesUserStatus.COMPLETED, updated_at__year=current_year).count()
    completed_books_year = user_books.filter(status=BookStatus.COMPLETED, finish_date__year=current_year).count()
    completed_audiobooks_year = user_audiobooks.filter(status=AudiobookStatus.COMPLETED, finish_date__year=current_year).count()
    completed_comics_year = user_comics.filter(status=ComicMangaStatus.COMPLETED, finish_date__year=current_year).count()
    completed_games_year = user_games.filter(status=GameStatus.COMPLETED, finish_date__year=current_year).count()
    completed_boardgames_year = user_boardgames.filter(last_played__year=current_year).count()
    completed_exercises_year = user_tracks.filter(status=ExerciseTrackingStatus.COMPLETED, updated_at__year=current_year).count()

    total_items_year = (
        completed_movies_year +
        completed_series_year +
        completed_books_year +
        completed_audiobooks_year +
        completed_comics_year +
        completed_games_year +
        completed_boardgames_year +
        completed_exercises_year
    )
    # If 0 completions, count distinct active entries logged this year
    if total_items_year == 0:
        total_items_year = sum(1 for d in daily_activity_map if d.year == current_year)

    # Month Hours calculation
    month_minutes = 0

    # Movies watched this month
    for m in user_movies.filter(status=MovieStatus.COMPLETED, watch_date__gte=first_of_month):
        month_minutes += (m.runtime or 90)

    # Episodes logged this month
    for ep in user_episode_logs.filter(watched_at__date__gte=first_of_month):
        month_minutes += 45  # average standard television episode length

    # Audiobook progress this month
    for ab in user_audiobooks.filter(updated_at__date__gte=first_of_month):
        month_minutes += (ab.current_progress_minutes or 0)

    # Games playtime this month
    game_hours = 0
    for g in user_games.filter(updated_at__date__gte=first_of_month):
        game_hours += float(g.hours_played or 0)
    month_minutes += int(game_hours * 60)

    # Board games playtime
    for bg in user_boardgames.filter(last_played__gte=first_of_month):
        month_minutes += (bg.avg_session_minutes or bg.min_playtime or 45)

    # Exercises duration this month
    for ex in user_exercise_logs.filter(logged_date__gte=first_of_month):
        month_minutes += (ex.duration_minutes or 30)

    hours_consumed_month = round(month_minutes / 60.0, 1)
    days_in_month_so_far = max(1, today.day)
    daily_average_min = round(month_minutes / float(days_in_month_so_far))

    metrics = {
        "active_streak_days": streak,
        "total_items_year": total_items_year,
        "hours_consumed_month": hours_consumed_month,
        "daily_average_min": daily_average_min,
    }

    # -------------------------------------------------------------------------
    # 5. 52-Week Life Activity Heatmap
    # -------------------------------------------------------------------------
    start_date = today - timedelta(days=364)
    # Align to end on Saturday or smooth week boundary matching existing template
    heatmap_weeks = []
    current_day = start_date

    for w in range(52):
        week_days = []
        for d in range(7):
            entry = daily_activity_map.get(current_day)
            count = entry["count"] if entry else 0
            items_str = ", ".join(entry["items"][:3]) if entry else ""
            if entry and len(entry["items"]) > 3:
                items_str += f" (+{len(entry['items']) - 3} more)"

            if count == 0:
                intensity = 0
                summary = "No activities logged"
            elif count == 1:
                intensity = 1
                summary = f"1 activity ({items_str})"
            elif count == 2:
                intensity = 2
                summary = f"2 activities ({items_str})"
            elif count <= 4:
                intensity = 3
                summary = f"{count} activities ({items_str})"
            else:
                intensity = 4
                summary = f"{count} activities (High engagement day! {items_str})"

            week_days.append({
                "date": current_day.strftime("%b %d, %Y"),
                "iso_date": current_day.isoformat(),
                "intensity": intensity,
                "count": count,
                "summary": summary,
                "month_name": current_day.strftime("%b") if current_day.day <= 7 and d == 0 else ""
            })
            current_day += timedelta(days=1)
        heatmap_weeks.append(week_days)

    # -------------------------------------------------------------------------
    # 6. Currently In-Progress Items
    # -------------------------------------------------------------------------
    in_progress = []

    # Series (WATCHING)
    for s in user_series.filter(user_status=SeriesUserStatus.WATCHING)[:2]:
        tot_ep = s.total_episodes or 10
        cur_ep = s.current_episode_number or 0
        pct = min(100, int((cur_ep / tot_ep) * 100)) if tot_ep > 0 else 0
        in_progress.append({
            "id": f"s-{s.id}",
            "category": "series",
            "category_label": "Series",
            "category_badge": "bg-indigo-500/15 text-indigo-400 border-indigo-500/30",
            "title": s.title,
            "subtitle": f"Season {s.current_season_number} &bull; Episode {s.current_episode_number}",
            "cover_url": s.poster_url,
            "percent": pct,
            "progress_text": f"Episode {cur_ep} of {tot_ep}",
            "last_updated": s.updated_at.strftime("%b %d"),
            "action_label": "+1 Ep",
            "detail_url": f"/series/{s.id}/",
        })

    # Movies (WATCHING)
    for m in user_movies.filter(status=MovieStatus.WATCHING)[:2]:
        in_progress.append({
            "id": f"m-{m.id}",
            "category": "movies",
            "category_label": "Movie",
            "category_badge": "bg-amber-500/15 text-amber-400 border-amber-500/30",
            "title": m.title,
            "subtitle": f"{m.director or 'Feature Film'} &bull; {m.runtime or 120} mins",
            "cover_url": m.poster_url,
            "percent": 50,
            "progress_text": f"Watching ({m.runtime or 120}m)",
            "last_updated": m.updated_at.strftime("%b %d"),
            "action_label": "Details",
            "detail_url": f"/movies/{m.id}/",
        })

    # Books (READING)
    for b in user_books.filter(status=BookStatus.READING)[:2]:
        tot_p = b.page_count or 100
        cur_p = b.current_page or 0
        pct = min(100, int((cur_p / tot_p) * 100)) if tot_p > 0 else 0
        in_progress.append({
            "id": f"b-{b.id}",
            "category": "books",
            "category_label": "Book",
            "category_badge": "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
            "title": b.title,
            "subtitle": f"{b.author or 'Author Unlisted'}",
            "cover_url": b.display_cover,
            "percent": pct,
            "progress_text": f"Page {cur_p} of {tot_p}",
            "last_updated": b.updated_at.strftime("%b %d"),
            "action_label": "+10 pgs",
            "detail_url": f"/books/{b.id}/",
        })

    # Audiobooks (LISTENING)
    for ab in user_audiobooks.filter(status=AudiobookStatus.LISTENING)[:2]:
        tot_m = ab.duration_minutes or 300
        cur_m = ab.current_progress_minutes or 0
        pct = min(100, int((cur_m / tot_m) * 100)) if tot_m > 0 else 0
        in_progress.append({
            "id": f"ab-{ab.id}",
            "category": "audiobooks",
            "category_label": "Audiobook",
            "category_badge": "bg-violet-500/15 text-violet-400 border-violet-500/30",
            "title": ab.title,
            "subtitle": f"Narrated by {ab.narrator or ab.author or 'Narrator'}",
            "cover_url": ab.display_cover,
            "percent": pct,
            "progress_text": f"{round(cur_m / 60.0, 1)}h of {round(tot_m / 60.0, 1)}h",
            "last_updated": ab.updated_at.strftime("%b %d"),
            "action_label": "+15 min",
            "detail_url": f"/audiobooks/{ab.id}/",
        })

    # Comics (READING)
    for c in user_comics.filter(status=ComicMangaStatus.READING)[:2]:
        tot_ch = c.total_chapters or 50
        cur_ch = c.current_chapter or 0
        pct = min(100, int((cur_ch / tot_ch) * 100)) if tot_ch > 0 else 0
        in_progress.append({
            "id": f"c-{c.id}",
            "category": "comics",
            "category_label": "Comics / Manga",
            "category_badge": "bg-rose-500/15 text-rose-400 border-rose-500/30",
            "title": c.title,
            "subtitle": f"{c.creator_author or 'Author'} &bull; {c.get_item_type_display()}",
            "cover_url": c.display_cover,
            "percent": pct,
            "progress_text": f"Chapter {cur_ch} of {tot_ch}",
            "last_updated": c.updated_at.strftime("%b %d"),
            "action_label": "+1 Ch",
            "detail_url": f"/comics/{c.id}/",
        })

    # Games (PLAYING)
    for g in user_games.filter(status=GameStatus.PLAYING)[:2]:
        in_progress.append({
            "id": f"g-{g.id}",
            "category": "games",
            "category_label": "Video Game",
            "category_badge": "bg-cyan-500/15 text-cyan-400 border-cyan-500/30",
            "title": g.title,
            "subtitle": f"{g.platform_played or g.platforms_available or 'PC / Console'}",
            "cover_url": g.display_cover,
            "percent": min(100, int((float(g.hours_played or 0) / 40.0) * 100)),
            "progress_text": f"{g.hours_played or 0}h played",
            "last_updated": g.updated_at.strftime("%b %d"),
            "action_label": "+30m",
            "detail_url": f"/games/{g.id}/",
        })

    # Board games (OWNED / PLAYED with sessions)
    for bg in user_boardgames.filter(status__in=[BoardGameStatus.PLAYED, BoardGameStatus.OWNED])[:1]:
        in_progress.append({
            "id": f"bg-{bg.id}",
            "category": "boardgames",
            "category_label": "Board Game",
            "category_badge": "bg-orange-500/15 text-orange-400 border-orange-500/30",
            "title": bg.title,
            "subtitle": f"{bg.player_count_display} &bull; {bg.playtime_display}",
            "cover_url": bg.display_cover,
            "percent": min(100, bg.play_count * 10),
            "progress_text": f"{bg.play_count} plays recorded",
            "last_updated": bg.updated_at.strftime("%b %d"),
            "action_label": "Log Play",
            "detail_url": f"/boardgames/{bg.id}/",
        })

    # Exercises (IN_PROGRESS)
    for track in user_tracks.filter(status=ExerciseTrackingStatus.IN_PROGRESS)[:2]:
        sessions_cnt = track.exercise.logs.filter(user=user).count()
        in_progress.append({
            "id": f"ex-{track.id}",
            "category": "exercises",
            "category_label": "Fitness Routine",
            "category_badge": "bg-teal-500/15 text-teal-400 border-teal-500/30",
            "title": track.exercise.name,
            "subtitle": track.personal_goal or f"Target: {track.exercise.get_target_muscle_group_display()}",
            "cover_url": "",
            "percent": min(100, sessions_cnt * 10),
            "progress_text": f"{sessions_cnt} sessions logged",
            "last_updated": track.updated_at.strftime("%b %d"),
            "action_label": "Log Session",
            "detail_url": f"/exercises/{track.exercise.slug}/",
        })

    # -------------------------------------------------------------------------
    # 7. Planned / Watchlist Queue ("Up Next")
    # -------------------------------------------------------------------------
    planned_queue = []

    for m in user_movies.filter(status=MovieStatus.PLAN_TO_WATCH)[:2]:
        planned_queue.append({
            "id": f"pl-m-{m.id}",
            "title": m.title,
            "category": "Movie",
            "category_badge": "bg-amber-500/10 text-amber-400 border-amber-500/20",
            "tag": "Plan to Watch",
            "note": m.tagline or m.overview[:80] or "Saved to watchlist",
            "release_year": str(m.release_date.year) if m.release_date else "Movie",
            "cover_url": m.poster_url,
            "detail_url": f"/movies/{m.id}/",
        })

    for s in user_series.filter(user_status=SeriesUserStatus.PLAN_TO_WATCH)[:2]:
        planned_queue.append({
            "id": f"pl-s-{s.id}",
            "title": s.title,
            "category": "Series",
            "category_badge": "bg-indigo-500/10 text-indigo-400 border-indigo-500/20",
            "tag": "Plan to Watch",
            "note": s.tagline or s.overview[:80] or "Queued series",
            "release_year": f"{s.total_seasons or 1} Seasons",
            "cover_url": s.poster_url,
            "detail_url": f"/series/{s.id}/",
        })

    for b in user_books.filter(status=BookStatus.PLAN_TO_READ)[:2]:
        planned_queue.append({
            "id": f"pl-b-{b.id}",
            "title": b.title,
            "category": "Book",
            "category_badge": "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
            "tag": "Want to Read",
            "note": b.description[:80] if b.description else "On reading queue",
            "release_year": b.author or "Book",
            "cover_url": b.display_cover,
            "detail_url": f"/books/{b.id}/",
        })

    for g in user_games.filter(status=GameStatus.BACKLOG)[:2]:
        planned_queue.append({
            "id": f"pl-g-{g.id}",
            "title": g.title,
            "category": "Game",
            "category_badge": "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
            "tag": "Backlog",
            "note": g.notes or "Queued in gaming backlog",
            "release_year": g.platform_played or "Game",
            "cover_url": g.display_cover,
            "detail_url": f"/games/{g.id}/",
        })

    for bg in user_boardgames.filter(status=BoardGameStatus.WANT_TO_PLAY)[:2]:
        planned_queue.append({
            "id": f"pl-bg-{bg.id}",
            "title": bg.title,
            "category": "Board Game",
            "category_badge": "bg-orange-500/10 text-orange-400 border-orange-500/20",
            "tag": "Want to Play",
            "note": bg.notes or f"Rank #{bg.bgg_rank}" if bg.bgg_rank else "Tabletop queue",
            "release_year": bg.player_count_display,
            "cover_url": bg.display_cover,
            "detail_url": f"/boardgames/{bg.id}/",
        })

    for tr in user_tracks.filter(status=ExerciseTrackingStatus.PLANNED)[:2]:
        planned_queue.append({
            "id": f"pl-ex-{tr.id}",
            "title": tr.exercise.name,
            "category": "Exercise",
            "category_badge": "bg-teal-500/10 text-teal-400 border-teal-500/20",
            "tag": "Planned",
            "note": tr.personal_goal or "Next movement in queue",
            "release_year": tr.exercise.get_target_muscle_group_display(),
            "cover_url": "",
            "detail_url": f"/exercises/{tr.exercise.slug}/",
        })

    # -------------------------------------------------------------------------
    # 8. Recently Completed / Finished Highlights
    # -------------------------------------------------------------------------
    recently_finished = []

    for m in user_movies.filter(status=MovieStatus.COMPLETED).order_by("-updated_at")[:2]:
        recently_finished.append({
            "id": f"rf-m-{m.id}",
            "title": m.title,
            "category": "Movie",
            "category_badge": "bg-amber-500/10 text-amber-400 border-amber-500/20",
            "completed_date": m.watch_date.strftime("%b %d, %Y") if m.watch_date else m.updated_at.strftime("%b %d, %Y"),
            "rating": m.rating or 0,
            "rating_stars": _make_stars(m.rating),
            "review": m.review or "Completed and chronicled.",
            "cover_url": m.poster_url,
            "detail_url": f"/movies/{m.id}/",
        })

    for s in user_series.filter(user_status=SeriesUserStatus.COMPLETED).order_by("-updated_at")[:2]:
        recently_finished.append({
            "id": f"rf-s-{s.id}",
            "title": s.title,
            "category": "Series",
            "category_badge": "bg-indigo-500/10 text-indigo-400 border-indigo-500/20",
            "completed_date": s.updated_at.strftime("%b %d, %Y"),
            "rating": s.rating or 0,
            "rating_stars": _make_stars(s.rating),
            "review": s.review or "Series finished.",
            "cover_url": s.poster_url,
            "detail_url": f"/series/{s.id}/",
        })

    for b in user_books.filter(status=BookStatus.COMPLETED).order_by("-updated_at")[:2]:
        recently_finished.append({
            "id": f"rf-b-{b.id}",
            "title": b.title,
            "category": "Book",
            "category_badge": "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
            "completed_date": b.finish_date.strftime("%b %d, %Y") if b.finish_date else b.updated_at.strftime("%b %d, %Y"),
            "rating": b.rating or 0,
            "rating_stars": _make_stars(b.rating),
            "review": b.review or "Book completed.",
            "cover_url": b.display_cover,
            "detail_url": f"/books/{b.id}/",
        })

    for ab in user_audiobooks.filter(status=AudiobookStatus.COMPLETED).order_by("-updated_at")[:2]:
        recently_finished.append({
            "id": f"rf-ab-{ab.id}",
            "title": ab.title,
            "category": "Audiobook",
            "category_badge": "bg-violet-500/10 text-violet-400 border-violet-500/20",
            "completed_date": ab.finish_date.strftime("%b %d, %Y") if ab.finish_date else ab.updated_at.strftime("%b %d, %Y"),
            "rating": ab.rating or 0,
            "rating_stars": _make_stars(ab.rating),
            "review": ab.review or "Audiobook finished.",
            "cover_url": ab.display_cover,
            "detail_url": f"/audiobooks/{ab.id}/",
        })

    for g in user_games.filter(status=GameStatus.COMPLETED).order_by("-updated_at")[:2]:
        recently_finished.append({
            "id": f"rf-g-{g.id}",
            "title": g.title,
            "category": "Game",
            "category_badge": "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
            "completed_date": g.finish_date.strftime("%b %d, %Y") if g.finish_date else g.updated_at.strftime("%b %d, %Y"),
            "rating": g.rating or 0,
            "rating_stars": _make_stars(g.rating),
            "review": g.review or f"Completed with {g.hours_played or 0} hours played.",
            "cover_url": g.display_cover,
            "detail_url": f"/games/{g.id}/",
        })

    return {
        "username": user.username,
        "metrics": metrics,
        "heatmap_weeks": heatmap_weeks,
        "in_progress": in_progress,
        "recently_finished": recently_finished[:6],
        "planned_queue": planned_queue[:6],
    }
