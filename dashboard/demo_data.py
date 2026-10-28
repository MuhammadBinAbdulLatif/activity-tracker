import random
from datetime import datetime, timedelta

def get_demo_dashboard_data(username="ChronicleUser"):
    """
    Returns rich, realistic demo data for the uTrack home dashboard.
    Will be replaced in subsequent phases by real ORM queries.
    """
    # 1. Summary Metrics
    metrics = {
        "active_streak_days": 18,
        "total_items_year": 142,
        "hours_consumed_month": 56.4,
        "daily_average_min": 112,
    }

    # 2. Daily Heatmap (GitHub-style 52-week calendar grid)
    # Generate 52 weeks (364 days + current remaining days) leading up to today
    today = datetime.now().date()
    # Align to end on the most recent Saturday or today's weekday
    # 52 weeks * 7 days = 364 days
    start_date = today - timedelta(days=364)
    
    # We will build a list of weeks, where each week is a list of 7 day dicts
    # Day dict: { "date": "YYYY-MM-DD", "day_num": int, "intensity": 0-4, "count": int, "summary": str }
    heatmap_weeks = []
    current_day = start_date
    
    # Let's seed predictable or organic feeling intensity patterns
    random.seed(42) # Consistent realistic render for demo
    
    for w in range(52):
        week_days = []
        for d in range(7):
            # Weighted random intensity
            # Intensity 0: ~25%, 1: ~30%, 2: ~25%, 3: ~12%, 4: ~8%
            rand_val = random.random()
            if rand_val < 0.22:
                intensity = 0
                count = 0
                summary = "No activities logged"
            elif rand_val < 0.55:
                intensity = 1
                count = random.randint(1, 2)
                summary = f"{count} activity logged (30m reading)"
            elif rand_val < 0.82:
                intensity = 2
                count = random.randint(2, 4)
                summary = f"{count} activities (1 movie watched, 25 pages read)"
            elif rand_val < 0.94:
                intensity = 3
                count = random.randint(4, 6)
                summary = f"{count} activities (2 episodes, 45 pages, 1 workout)"
            else:
                intensity = 4
                count = random.randint(6, 8)
                summary = f"{count} activities (High engagement day! 3 episodes, 1 book finished, run)"

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

    # 3. Currently Watching / Reading / Listening / Tracking (In-Progress)
    in_progress = [
        {
            "id": "ip-1",
            "category": "series",
            "category_label": "Series",
            "category_badge": "bg-indigo-500/15 text-indigo-400 border-indigo-500/30",
            "icon": "tv",
            "title": "Severance",
            "subtitle": "Season 2 &bull; Episode 5: 'The Grim Barbarity'",
            "cover_url": "https://images.unsplash.com/photo-1518791841217-8f162f1e1131?auto=format&fit=crop&w=600&q=80",
            "current_progress": 5,
            "total_progress": 10,
            "unit": "Episodes",
            "percent": 50,
            "progress_text": "Episode 5 of 10",
            "last_updated": "Yesterday",
            "badge_color": "indigo",
            "action_label": "+1 Ep",
        },
        {
            "id": "ip-2",
            "category": "movies",
            "category_label": "Movie",
            "category_badge": "bg-amber-500/15 text-amber-400 border-amber-500/30",
            "icon": "film",
            "title": "Dune: Part Two",
            "subtitle": "Directed by Denis Villeneuve &bull; Sci-Fi",
            "cover_url": "https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&w=600&q=80",
            "current_progress": 94,
            "total_progress": 166,
            "unit": "Minutes",
            "percent": 57,
            "progress_text": "1h 34m of 2h 46m",
            "last_updated": "2 hours ago",
            "badge_color": "amber",
            "action_label": "Resume",
        },
        {
            "id": "ip-3",
            "category": "books",
            "category_label": "Book",
            "category_badge": "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
            "icon": "book-open",
            "title": "Project Hail Mary",
            "subtitle": "Andy Weir &bull; Sci-Fi Hard Novel",
            "cover_url": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80",
            "current_progress": 312,
            "total_progress": 496,
            "unit": "Pages",
            "percent": 63,
            "progress_text": "Page 312 of 496",
            "last_updated": "Today at 08:30 AM",
            "badge_color": "emerald",
            "action_label": "+10 pgs",
        },
        {
            "id": "ip-4",
            "category": "audiobooks",
            "category_label": "Audiobook",
            "category_badge": "bg-violet-500/15 text-violet-400 border-violet-500/30",
            "icon": "headphones",
            "title": "Atomic Habits",
            "subtitle": "James Clear &bull; Narrated by Author (1.2x speed)",
            "cover_url": "https://images.unsplash.com/photo-1543002588-bfa74002ed7e?auto=format&fit=crop&w=600&q=80",
            "current_progress": 3.8,
            "total_progress": 5.5,
            "unit": "Hours",
            "percent": 69,
            "progress_text": "3h 48m of 5h 30m (Chapter 14)",
            "last_updated": "3 days ago",
            "badge_color": "violet",
            "action_label": "+15 min",
        },
        {
            "id": "ip-5",
            "category": "comics",
            "category_label": "Comics / Manga",
            "category_badge": "bg-rose-500/15 text-rose-400 border-rose-500/30",
            "icon": "sparkles",
            "title": "Berserk: Deluxe Edition",
            "subtitle": "Kentaro Miura &bull; Volume 7 (Conviction Arc)",
            "cover_url": "https://images.unsplash.com/photo-1563089145-599997674d42?auto=format&fit=crop&w=600&q=80",
            "current_progress": 182,
            "total_progress": 364,
            "unit": "Chapters",
            "percent": 50,
            "progress_text": "Chapter 182 of 364",
            "last_updated": "4 days ago",
            "badge_color": "rose",
            "action_label": "+1 Ch",
        },
        {
            "id": "ip-6",
            "category": "exercises",
            "category_label": "Habit & Fitness",
            "category_badge": "bg-teal-500/15 text-teal-400 border-teal-500/30",
            "icon": "activity",
            "title": "5K Strength & Endurance Routine",
            "subtitle": "Weekly Target: 4 Sessions",
            "cover_url": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=600&q=80",
            "current_progress": 3,
            "total_progress": 4,
            "unit": "Sessions",
            "percent": 75,
            "progress_text": "3 of 4 workouts completed",
            "last_updated": "Yesterday",
            "badge_color": "teal",
            "action_label": "Log Session",
        },
    ]

    # 4. Recently Finished / Retrospective Highlights
    recently_finished = [
        {
            "id": "rf-1",
            "title": "Oppenheimer",
            "category": "Movie",
            "category_badge": "bg-amber-500/10 text-amber-400 border-amber-500/20",
            "completed_date": "Oct 24, 2026",
            "rating": 5,
            "rating_stars": "★★★★★",
            "review": "Masterful pacing and sonic design. The Trinity test sequence and interrogation close-ups were breathtaking.",
            "cover_url": "https://images.unsplash.com/photo-1485846234645-a62644f84728?auto=format&fit=crop&w=400&q=80",
        },
        {
            "id": "rf-2",
            "title": "Klara and the Sun",
            "category": "Book",
            "category_badge": "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
            "completed_date": "Oct 20, 2026",
            "rating": 4.5,
            "rating_stars": "★★★★½",
            "review": "A poignant, gentle exploration of what it means to love through the quiet eyes of an artificial friend.",
            "cover_url": "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?auto=format&fit=crop&w=400&q=80",
        },
        {
            "id": "rf-3",
            "title": "Shogun (Mini-Series)",
            "category": "Series",
            "category_badge": "bg-indigo-500/10 text-indigo-400 border-indigo-500/20",
            "completed_date": "Oct 15, 2026",
            "rating": 5,
            "rating_stars": "★★★★★",
            "review": "Immaculate production value, nuanced court intrigue, and incredible performances by Sanada and Sawai.",
            "cover_url": "https://images.unsplash.com/photo-1578632767115-351597cf2477?auto=format&fit=crop&w=400&q=80",
        },
        {
            "id": "rf-4",
            "title": "Sapiens: A Brief History of Humankind",
            "category": "Audiobook",
            "category_badge": "bg-violet-500/10 text-violet-400 border-violet-500/20",
            "completed_date": "Oct 09, 2026",
            "rating": 4,
            "rating_stars": "★★★★☆",
            "review": "Thought-provoking overview of cognitive and agricultural revolutions. Kept me engaged on long commutes.",
            "cover_url": "https://images.unsplash.com/photo-1457369804613-52c61a468e7d?auto=format&fit=crop&w=400&q=80",
        },
    ]

    # 5. Planned / Watchlist Queue ("Up Next")
    planned_queue = [
        {
            "id": "pl-1",
            "title": "Interstellar",
            "category": "Movie",
            "category_badge": "bg-amber-500/10 text-amber-400 border-amber-500/20",
            "tag": "High Priority",
            "note": "Planned for Friday movie night rewatch in 4K.",
            "release_year": "2014",
            "cover_url": "https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?auto=format&fit=crop&w=400&q=80",
        },
        {
            "id": "pl-2",
            "title": "Children of Time",
            "category": "Book",
            "category_badge": "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
            "tag": "Next Read",
            "note": "Recommended by Arthur for great evolutionary sci-fi world-building.",
            "release_year": "Adrian Tchaikovsky",
            "cover_url": "https://images.unsplash.com/photo-1532012164546-f432f2e3777f?auto=format&fit=crop&w=400&q=80",
        },
        {
            "id": "pl-3",
            "title": "Arcane: Season 2",
            "category": "Series",
            "category_badge": "bg-indigo-500/10 text-indigo-400 border-indigo-500/20",
            "tag": "Anticipated",
            "note": "Queued for release binge watch.",
            "release_year": "Animation &bull; Netflix",
            "cover_url": "https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?auto=format&fit=crop&w=400&q=80",
        },
        {
            "id": "pl-4",
            "title": "Chainsaw Man (Part 2)",
            "category": "Comics",
            "category_badge": "bg-rose-500/10 text-rose-400 border-rose-500/20",
            "tag": "Manga",
            "note": "Catch up on Academy saga.",
            "release_year": "Tatsuki Fujimoto",
            "cover_url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=400&q=80",
        },
    ]

    return {
        "username": username,
        "metrics": metrics,
        "heatmap_weeks": heatmap_weeks,
        "in_progress": in_progress,
        "recently_finished": recently_finished,
        "planned_queue": planned_queue,
    }
