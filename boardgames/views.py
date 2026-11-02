from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from django.contrib import messages

from .models import BoardGameEntry, BoardGameStatus
from .forms import BoardGameEntryForm
from services.boardgame_service import BoardGameService


# --------------------------------------------------------------------------- #
# List View
# --------------------------------------------------------------------------- #

@login_required
def boardgame_list(request: HttpRequest) -> HttpResponse:
    entries = BoardGameEntry.objects.filter(user=request.user)

    played = entries.filter(status=BoardGameStatus.PLAYED)
    owned = entries.filter(status=BoardGameStatus.OWNED)
    want_to_play = entries.filter(status=BoardGameStatus.WANT_TO_PLAY)
    wishlist = entries.filter(status=BoardGameStatus.WISHLIST)
    traded_away = entries.filter(status=BoardGameStatus.TRADED_AWAY)

    # Aggregates
    total_tracked = entries.count()
    total_sessions = sum(e.play_count for e in entries)
    unique_played_count = entries.filter(play_count__gt=0).count()
    owned_count = owned.count()

    context = {
        "entries": entries,
        "played": played,
        "owned": owned,
        "want_to_play": want_to_play,
        "wishlist": wishlist,
        "traded_away": traded_away,
        "total_tracked": total_tracked,
        "total_sessions": total_sessions,
        "unique_played_count": unique_played_count,
        "owned_count": owned_count,
        "form": BoardGameEntryForm(),
        "statuses": BoardGameStatus,
    }
    return render(request, "boardgames/list.html", context)


# --------------------------------------------------------------------------- #
# Live Search (HTMX)
# --------------------------------------------------------------------------- #

@login_required
def search_boardgames(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("q", "").strip()
    results = []

    if query:
        results = BoardGameService.search(query, limit=10)

        # Mark already tracked items
        tracked_ids = set(
            BoardGameEntry.objects.filter(
                user=request.user,
                external_id__in=[r["external_id"] for r in results if r.get("external_id")]
            ).values_list("external_id", flat=True)
        )
        for r in results:
            r["is_tracked"] = r.get("external_id") in tracked_ids

    return render(
        request,
        "boardgames/partials/search_results.html",
        {"results": results, "query": query}
    )


# --------------------------------------------------------------------------- #
# Add Board Game (Quick search add or manual form)
# --------------------------------------------------------------------------- #

@login_required
@require_POST
def add_boardgame(request: HttpRequest) -> HttpResponse:
    external_id = request.POST.get("external_id", "").strip()
    title = request.POST.get("title", "").strip()
    status_val = request.POST.get("status", BoardGameStatus.WANT_TO_PLAY)

    if title and external_id:
        # Search-enriched quick-add path: fetch rich BGG metadata
        bgg_details = BoardGameService.get_details(external_id)

        entry = BoardGameEntry(
            user=request.user,
            external_id=external_id,
            title=bgg_details.get("title") or title,
            cover_url=bgg_details.get("cover_url") or request.POST.get("cover_url", ""),
            description=bgg_details.get("description", ""),
            year_published=bgg_details.get("year_published") or (int(request.POST.get("year_published")) if request.POST.get("year_published", "").isdigit() else None),
            min_players=bgg_details.get("min_players"),
            max_players=bgg_details.get("max_players"),
            min_playtime=bgg_details.get("min_playtime"),
            max_playtime=bgg_details.get("max_playtime"),
            designers=bgg_details.get("designers", ""),
            publishers=bgg_details.get("publishers", ""),
            categories=bgg_details.get("categories", ""),
            mechanics=bgg_details.get("mechanics", ""),
            bgg_rating=bgg_details.get("bgg_rating"),
            bgg_rank=bgg_details.get("bgg_rank"),
            status=status_val if status_val in BoardGameStatus.values else BoardGameStatus.WANT_TO_PLAY,
        )
        entry.save()
        messages.success(request, f"Added '{entry.title}' to your shelf!")
        return redirect("boardgame_detail", pk=entry.pk)

    # Manual form submission
    form = BoardGameEntryForm(request.POST, request.FILES)
    if form.is_valid():
        entry = form.save(commit=False)
        entry.user = request.user
        entry.save()
        messages.success(request, f"Created entry for '{entry.title}'!")
        return redirect("boardgame_detail", pk=entry.pk)

    # Form errors
    messages.error(request, "Failed to add board game. Please review the errors below.")
    entries = BoardGameEntry.objects.filter(user=request.user)
    context = {
        "entries": entries,
        "played": entries.filter(status=BoardGameStatus.PLAYED),
        "owned": entries.filter(status=BoardGameStatus.OWNED),
        "want_to_play": entries.filter(status=BoardGameStatus.WANT_TO_PLAY),
        "wishlist": entries.filter(status=BoardGameStatus.WISHLIST),
        "traded_away": entries.filter(status=BoardGameStatus.TRADED_AWAY),
        "total_tracked": entries.count(),
        "total_sessions": sum(e.play_count for e in entries),
        "unique_played_count": entries.filter(play_count__gt=0).count(),
        "owned_count": entries.filter(status=BoardGameStatus.OWNED).count(),
        "form": form,
        "statuses": BoardGameStatus,
    }
    return render(request, "boardgames/list.html", context, status=400)


# --------------------------------------------------------------------------- #
# Detail View
# --------------------------------------------------------------------------- #

@login_required
def boardgame_detail(request: HttpRequest, pk: int) -> HttpResponse:
    entry = get_object_or_404(BoardGameEntry, pk=pk, user=request.user)
    form = BoardGameEntryForm(instance=entry)
    context = {
        "entry": entry,
        "form": form,
        "statuses": BoardGameStatus,
    }
    return render(request, "boardgames/detail.html", context)


# --------------------------------------------------------------------------- #
# Quick Log Play Action
# --------------------------------------------------------------------------- #

@login_required
@require_POST
def log_play(request: HttpRequest, pk: int) -> HttpResponse:
    entry = get_object_or_404(BoardGameEntry, pk=pk, user=request.user)
    entry.play_count += 1
    entry.last_played = timezone.now().date()
    if entry.status in [BoardGameStatus.WANT_TO_PLAY, BoardGameStatus.WISHLIST]:
        entry.status = BoardGameStatus.PLAYED
    entry.save()

    messages.success(request, f"Logged play for '{entry.title}'. Total plays: {entry.play_count}")
    return redirect("boardgame_detail", pk=entry.pk)


# --------------------------------------------------------------------------- #
# Update Details
# --------------------------------------------------------------------------- #

@login_required
@require_POST
def update_boardgame_details(request: HttpRequest, pk: int) -> HttpResponse:
    entry = get_object_or_404(BoardGameEntry, pk=pk, user=request.user)
    form = BoardGameEntryForm(request.POST, request.FILES, instance=entry)
    if form.is_valid():
        form.save()
        messages.success(request, f"Updated '{entry.title}' successfully.")
    else:
        messages.error(request, "Could not update board game details. Check field errors.")
    return redirect("boardgame_detail", pk=entry.pk)


# --------------------------------------------------------------------------- #
# Delete Entry
# --------------------------------------------------------------------------- #

@login_required
@require_POST
def delete_boardgame(request: HttpRequest, pk: int) -> HttpResponse:
    entry = get_object_or_404(BoardGameEntry, pk=pk, user=request.user)
    title = entry.title
    entry.delete()
    messages.info(request, f"Removed '{title}' from your chronicle.")
    return redirect("boardgame_list")
