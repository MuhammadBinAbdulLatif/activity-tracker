from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpRequest, JsonResponse
from django.contrib import messages
from decimal import Decimal, InvalidOperation

from .models import GameEntry, GameStatus
from .forms import GameEntryForm
from services.videogame_service import VideoGameService


# --------------------------------------------------------------------------- #
# List View
# --------------------------------------------------------------------------- #

@login_required
def game_list(request: HttpRequest):
    entries = GameEntry.objects.filter(user=request.user)

    playing   = entries.filter(status=GameStatus.PLAYING)
    backlog   = entries.filter(status=GameStatus.BACKLOG)
    completed = entries.filter(status=GameStatus.COMPLETED)
    on_hold   = entries.filter(status=GameStatus.ON_HOLD)
    dropped   = entries.filter(status=GameStatus.DROPPED)

    total_hours = sum(e.hours_played for e in entries)

    context = {
        "playing": playing,
        "backlog": backlog,
        "completed": completed,
        "on_hold": on_hold,
        "dropped": dropped,
        "total_tracked": entries.count(),
        "total_hours": total_hours,
        "currently_playing_count": playing.count(),
        "completed_count": completed.count(),
        "form": GameEntryForm(),
        "statuses": GameStatus,
    }
    return render(request, "games/list.html", context)


# --------------------------------------------------------------------------- #
# Live Search (HTMX)
# --------------------------------------------------------------------------- #

@login_required
def search_games(request: HttpRequest):
    query = request.GET.get("q", "").strip()
    results = []

    if query:
        results = VideoGameService.search(query, limit=10)

        # Mark already-tracked items (ignore DROPPED)
        tracked_ids = set(
            GameEntry.objects.filter(
                user=request.user,
                external_id__in=[r["external_id"] for r in results],
            ).exclude(status=GameStatus.DROPPED).values_list("external_id", flat=True)
        )
        for r in results:
            r["is_tracked"] = r["external_id"] in tracked_ids

    return render(request, "games/partials/search_results.html", {"results": results, "query": query})


# --------------------------------------------------------------------------- #
# Add Game
# --------------------------------------------------------------------------- #

@login_required
@require_POST
def add_game(request: HttpRequest):
    """
    Handles both search-enriched quick-adds and full manual form submission.
    Quick-add: hidden fields pre-filled from the search result JS/HTMX POST.
    Manual add: full GameEntryForm.
    """
    # Detect quick-add from search result (has 'external_id' and 'title' hidden fields)
    external_id = request.POST.get("external_id", "").strip()
    title = request.POST.get("title", "").strip()
    status_val = request.POST.get("status", GameStatus.BACKLOG)

    if title and external_id:
        # Quick add path — enrich details from RAWG if possible
        entry_data = {
            "external_id": external_id,
            "title": title,
            "cover_url": request.POST.get("cover_url", ""),
            "release_year": request.POST.get("release_year") or None,
            "developers": request.POST.get("developers", ""),
            "publishers": request.POST.get("publishers", ""),
            "genres": request.POST.get("genres", ""),
            "platforms_available": request.POST.get("platforms", ""),
            "description": request.POST.get("description", ""),
            "status": status_val,
        }

        # Try to fetch full details for richer metadata
        if external_id.startswith("rawg-"):
            rawg_id = external_id.replace("rawg-", "")
            detail = VideoGameService.get_details_rawg(rawg_id)
            if detail:
                entry_data.update({
                    "description": detail.get("description", entry_data["description"]),
                    "developers": detail.get("developers", entry_data["developers"]),
                    "publishers": detail.get("publishers", entry_data["publishers"]),
                    "genres": detail.get("genres", entry_data["genres"]),
                    "platforms_available": detail.get("platforms", entry_data["platforms_available"]),
                })

        # Clamp release_year safely
        try:
            entry_data["release_year"] = int(entry_data["release_year"]) if entry_data["release_year"] else None
        except (ValueError, TypeError):
            entry_data["release_year"] = None

        entry = GameEntry(user=request.user, **entry_data)
        entry.save()
        messages.success(request, f"Added '{entry.title}' to your game chronicle.")
        return redirect("game_detail", pk=entry.pk)

    # Full manual form path
    form = GameEntryForm(request.POST, request.FILES)
    if form.is_valid():
        entry = form.save(commit=False)
        entry.user = request.user
        entry.save()
        messages.success(request, f"Created custom game '{entry.title}'.")
        return redirect("game_detail", pk=entry.pk)

    # Form errors — show specific field error message
    error_parts = []
    for field, err_list in form.errors.items():
        field_label = form.fields[field].label or field.replace('_', ' ').title() if field in form.fields else field
        error_parts.append(f"{field_label}: {err_list[0]}")
    error_msg = "; ".join(error_parts) if error_parts else "Please check the form fields."
    messages.error(request, f"Could not create game: {error_msg}")
    return redirect("game_list")


# --------------------------------------------------------------------------- #
# Detail View
# --------------------------------------------------------------------------- #

@login_required
def game_detail(request: HttpRequest, pk: int):
    entry = get_object_or_404(GameEntry, pk=pk, user=request.user)
    form = GameEntryForm(instance=entry)
    context = {
        "entry": entry,
        "form": form,
        "statuses": GameStatus,
    }
    return render(request, "games/detail.html", context)


# --------------------------------------------------------------------------- #
# Update Details
# --------------------------------------------------------------------------- #

@login_required
@require_POST
def update_game_details(request: HttpRequest, pk: int):
    entry = get_object_or_404(GameEntry, pk=pk, user=request.user)
    form = GameEntryForm(request.POST, request.FILES, instance=entry)
    if form.is_valid():
        form.save()
        messages.success(request, f"Updated details for '{entry.title}'.")
        return redirect("game_detail", pk=pk)
    first_error = next(iter(form.errors.values()))[0] if form.errors else "Please check the form fields."
    messages.error(request, f"Could not update game: {first_error}")
    return redirect("game_detail", pk=pk)


# --------------------------------------------------------------------------- #
# Delete
# --------------------------------------------------------------------------- #

@login_required
@require_POST
def delete_game(request: HttpRequest, pk: int):
    entry = get_object_or_404(GameEntry, pk=pk, user=request.user)
    title = entry.title
    entry.delete()
    messages.success(request, f"Removed '{title}' from your chronicle.")
    return redirect("game_list")


# --------------------------------------------------------------------------- #
# Quick Update — hours & completion inline (from list OR detail card)
# --------------------------------------------------------------------------- #

@login_required
@require_POST
def quick_update_game(request: HttpRequest, pk: int):
    """
    Lightweight endpoint for the quick-log controls on the list / detail cards.
    Accepts:
        delta_hours      — decimal hours to add/subtract (+0.5, -0.5, etc.)
        add_hours        — (legacy/fallback) decimal hours to ADD
        set_completion   — integer 0–100 to SET as completion %
        set_status       — GameStatus value to switch status
    Always redirects back to the referer (or game_list).
    """
    entry = get_object_or_404(GameEntry, pk=pk, user=request.user)
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "game_list"

    # Support delta_hours (+0.5 or -0.5 for +30m / -30m) or add_hours
    delta_str = request.POST.get("delta_hours", "").strip() or request.POST.get("add_hours", "").strip()
    if delta_str:
        try:
            delta = Decimal(delta_str)
            # Cannot drop below 0 hours
            entry.hours_played = max(Decimal("0.0"), entry.hours_played + delta)
        except InvalidOperation:
            pass

    set_completion = request.POST.get("set_completion", "").strip()
    if set_completion:
        try:
            pct = int(set_completion)
            entry.completion_percentage = max(0, min(100, pct))
            # Auto-complete if 100% and currently playing
            if entry.completion_percentage == 100 and entry.status == GameStatus.PLAYING:
                entry.status = GameStatus.COMPLETED
        except ValueError:
            pass

    set_status = request.POST.get("set_status", "").strip()
    if set_status and set_status in GameStatus.values:
        entry.status = set_status

    entry.save(update_fields=["hours_played", "completion_percentage", "status", "updated_at"])
    return redirect(next_url)
