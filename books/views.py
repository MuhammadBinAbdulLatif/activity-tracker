import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.utils import timezone
from .models import BookEntry, BookStatus, BookFormat
from services.openlibrary import openlibrary_service

@login_required
def book_list_view(request):
    """
    Renders the dedicated Books section categorized by Currently Reading,
    Reading Wishlist (Plan to Read), and Completed / Library.
    """
    entries = BookEntry.objects.filter(user=request.user)

    reading = entries.filter(status=BookStatus.READING)
    wishlist = entries.filter(status=BookStatus.PLAN_TO_READ)
    completed = entries.filter(status=BookStatus.COMPLETED)
    dropped = entries.filter(status=BookStatus.DROPPED)

    # Key statistics
    total_books_read = completed.count()
    total_pages_read = sum(b.current_page for b in entries)

    context = {
        "reading": reading,
        "wishlist": wishlist,
        "completed": completed,
        "dropped": dropped,
        "total_count": entries.count(),
        "total_books_read": total_books_read,
        "total_pages_read": total_pages_read,
        "format_choices": BookFormat.choices,
        "status_choices": BookStatus.choices,
    }
    return render(request, "books/list.html", context)

@login_required
def search_books_view(request):
    """
    Live HTMX or JSON search for books via Open Library.
    """
    query = request.GET.get("q", "").strip()
    if not query:
        return render(request, "books/partials/search_results.html", {"results": []})

    data = openlibrary_service.search_books(query, limit=10)
    results = data.get("results", [])

    # Check if user already tracks these openlibrary_keys or titles (excluding dropped items)
    tracked_keys = set(
        BookEntry.objects.filter(user=request.user, openlibrary_key__gt="")
        .exclude(status=BookStatus.DROPPED)
        .values_list("openlibrary_key", flat=True)
    )

    formatted_results = []
    for item in results:
        w_key = item.get("openlibrary_key", "")
        formatted_results.append({
            "openlibrary_key": w_key,
            "title": item.get("title"),
            "author": item.get("author"),
            "publish_year": item.get("publish_year") or "",
            "page_count": item.get("page_count") or 0,
            "cover_url": item.get("cover_url") or "",
            "isbn": item.get("isbn") or "",
            "genres": item.get("genres") or "",
            "is_tracked": w_key in tracked_keys if w_key else False,
        })

    if request.headers.get("HX-Request"):
        return render(request, "books/partials/search_results.html", {"results": formatted_results})
    return JsonResponse({"results": formatted_results})

@login_required
def add_book_view(request):
    """
    Tracks a book from Open Library or via manual entry.
    """
    if request.method == "POST":
        openlibrary_key = request.POST.get("openlibrary_key", "").strip()
        status = request.POST.get("status", BookStatus.PLAN_TO_READ)
        book_format = request.POST.get("book_format", BookFormat.PAPERBACK)
        rating = request.POST.get("rating") or None
        review = request.POST.get("review", "").strip()
        current_page = int(request.POST.get("current_page") or 0)
        mind_changing = request.POST.get("mind_changing_takeaways", "").strip()
        quotes = request.POST.get("favorite_quotes", "").strip()

        # If added from Open Library search
        if openlibrary_key:
            title = request.POST.get("title", "Untitled").strip()
            author = request.POST.get("author", "").strip()
            publish_year = request.POST.get("publish_year") or None
            page_count = int(request.POST.get("page_count") or 0)
            cover_url = request.POST.get("cover_url", "").strip()
            isbn = request.POST.get("isbn", "").strip()
            genres = request.POST.get("genres", "").strip()

            # Attempt to enrich description if work details are available
            work_details = openlibrary_service.get_book_details(openlibrary_key)
            description = ""
            if work_details:
                description = work_details.get("description", "")
                if not genres and work_details.get("genres"):
                    genres = work_details.get("genres")

            if status == BookStatus.COMPLETED and current_page == 0 and page_count > 0:
                current_page = page_count

            finish_date = timezone.now().date() if status == BookStatus.COMPLETED else None
            start_date = timezone.now().date() if status == BookStatus.READING else None

            entry, created = BookEntry.objects.update_or_create(
                user=request.user,
                openlibrary_key=openlibrary_key,
                defaults={
                    "title": title,
                    "author": author,
                    "publish_year": int(publish_year) if publish_year else None,
                    "page_count": page_count,
                    "cover_url": cover_url,
                    "isbn": isbn,
                    "genres": genres,
                    "description": description,
                    "status": status,
                    "book_format": book_format,
                    "current_page": current_page,
                    "rating": float(rating) if rating else None,
                    "review": review,
                    "mind_changing_takeaways": mind_changing,
                    "favorite_quotes": quotes,
                    "start_date": start_date,
                    "finish_date": finish_date,
                }
            )
            action = "Added" if created else "Updated"
            messages.success(request, f"{action} '{entry.title}' to your {entry.get_status_display()}.")
            return redirect("book_detail", book_id=entry.id)

        # Manual / Custom Book Entry
        title = request.POST.get("title", "").strip()
        if title:
            custom_cover = request.FILES.get("cover_file")
            page_count = int(request.POST.get("page_count") or 0)
            if status == BookStatus.COMPLETED and current_page == 0 and page_count > 0:
                current_page = page_count

            finish_date = timezone.now().date() if status == BookStatus.COMPLETED else None
            start_date = timezone.now().date() if status == BookStatus.READING else None

            entry = BookEntry.objects.create(
                user=request.user,
                title=title,
                author=request.POST.get("author", "").strip(),
                publish_year=int(request.POST.get("publish_year")) if request.POST.get("publish_year") else None,
                page_count=page_count,
                current_page=current_page,
                book_format=book_format,
                description=request.POST.get("description", "").strip(),
                genres=request.POST.get("genres", "").strip(),
                status=status,
                rating=float(rating) if rating else None,
                review=review,
                mind_changing_takeaways=mind_changing,
                favorite_quotes=quotes,
                is_custom=True,
                custom_cover=custom_cover,
                start_date=start_date,
                finish_date=finish_date,
            )
            messages.success(request, f"Created custom book entry '{entry.title}'.")
            return redirect("book_detail", book_id=entry.id)

    return redirect("book_list")

@login_required
def book_detail_view(request, book_id):
    """
    Dedicated view for a single book: shows reading progress meter, format,
    mind-changing takeaways, favorite quotes, review, rating, and status controls.
    """
    book = get_object_or_404(BookEntry, id=book_id, user=request.user)

    # Backfill synopsis if empty and openlibrary_key exists
    if not book.description and book.openlibrary_key:
        details = openlibrary_service.get_book_details(book.openlibrary_key)
        if details and details.get("description"):
            book.description = details.get("description")
            if not book.genres and details.get("genres"):
                book.genres = details.get("genres")
            book.save()

    context = {
        "book": book,
        "status_choices": BookStatus.choices,
        "format_choices": BookFormat.choices,
    }
    return render(request, "books/detail.html", context)

@login_required
def update_book_details_view(request, book_id):
    """
    Handles comprehensive updates to a book's personal reading notes,
    mind-changing insights, quotes, rating, progress, dates, and format.
    """
    book = get_object_or_404(BookEntry, id=book_id, user=request.user)

    if request.method == "POST":
        new_status = request.POST.get("status")
        book_format = request.POST.get("book_format")
        rating_input = request.POST.get("rating")
        review_input = request.POST.get("review", "")
        mind_input = request.POST.get("mind_changing_takeaways", "")
        quotes_input = request.POST.get("favorite_quotes", "")
        current_page_input = request.POST.get("current_page")
        page_count_input = request.POST.get("page_count")
        reread_input = request.POST.get("reread_count")
        start_date_input = request.POST.get("start_date")
        finish_date_input = request.POST.get("finish_date")

        # Update Status
        if new_status in [s[0] for s in BookStatus.choices]:
            book.status = new_status
            if new_status == BookStatus.COMPLETED:
                if not finish_date_input and not book.finish_date:
                    book.finish_date = timezone.now().date()
                if book.page_count and book.current_page < book.page_count:
                    book.current_page = book.page_count
            elif new_status == BookStatus.READING:
                if not start_date_input and not book.start_date:
                    book.start_date = timezone.now().date()

        # Update Format
        if book_format in [f[0] for f in BookFormat.choices]:
            book.book_format = book_format

        # Page count & current page
        if page_count_input and page_count_input.isdigit():
            book.page_count = int(page_count_input)
        if current_page_input and current_page_input.isdigit():
            val = int(current_page_input)
            if book.page_count > 0:
                book.current_page = min(val, book.page_count)
            else:
                book.current_page = val
            
            # If user reached total pages, auto-mark completed
            if book.page_count > 0 and book.current_page >= book.page_count and book.status != BookStatus.COMPLETED:
                book.status = BookStatus.COMPLETED
                if not book.finish_date:
                    book.finish_date = timezone.now().date()

        # Dates
        if start_date_input:
            try:
                book.start_date = timezone.datetime.strptime(start_date_input, "%Y-%m-%d").date()
            except ValueError:
                pass
        elif request.POST.get("clear_start_date") == "1":
            book.start_date = None

        if finish_date_input:
            try:
                book.finish_date = timezone.datetime.strptime(finish_date_input, "%Y-%m-%d").date()
            except ValueError:
                pass
        elif request.POST.get("clear_finish_date") == "1":
            book.finish_date = None

        # Rating
        if rating_input:
            try:
                book.rating = float(rating_input)
            except ValueError:
                pass
        elif rating_input == "":
            book.rating = None

        # Reviews & Mind Reflections
        book.review = review_input.strip()
        book.mind_changing_takeaways = mind_input.strip()
        book.favorite_quotes = quotes_input.strip()

        # Reread Counter
        if reread_input and reread_input.isdigit():
            book.reread_count = int(reread_input)

        # Custom book metadata updates
        if book.is_custom:
            if "title" in request.POST and request.POST["title"].strip():
                book.title = request.POST["title"].strip()
            if "author" in request.POST:
                book.author = request.POST["author"].strip()
            if "description" in request.POST:
                book.description = request.POST["description"].strip()
            if "genres" in request.POST:
                book.genres = request.POST["genres"].strip()
            if "cover_file" in request.FILES:
                book.custom_cover = request.FILES["cover_file"]

        book.save()
        messages.success(request, f"Updated notes and progress for '{book.title}'.")
        return redirect("book_detail", book_id=book.id)

    return redirect("book_detail", book_id=book.id)

@login_required
def update_book_progress_view(request, book_id):
    """
    Quick endpoint to increment or set reading page progress.
    Can be called via POST or AJAX.
    """
    book = get_object_or_404(BookEntry, id=book_id, user=request.user)
    if request.method == "POST":
        step = request.POST.get("step")
        page_val = request.POST.get("page")

        if step:
            try:
                book.current_page = max(0, book.current_page + int(step))
            except ValueError:
                pass
        elif page_val and page_val.isdigit():
            book.current_page = max(0, int(page_val))

        if book.page_count > 0:
            book.current_page = min(book.current_page, book.page_count)
            if book.current_page >= book.page_count and book.status != BookStatus.COMPLETED:
                book.status = BookStatus.COMPLETED
                if not book.finish_date:
                    book.finish_date = timezone.now().date()
            elif book.status == BookStatus.PLAN_TO_READ and book.current_page > 0:
                book.status = BookStatus.READING
                if not book.start_date:
                    book.start_date = timezone.now().date()

        book.save()

        if request.headers.get("HX-Request") or request.headers.get("Accept") == "application/json":
            return JsonResponse({
                "current_page": book.current_page,
                "page_count": book.page_count,
                "progress_percentage": book.progress_percentage,
                "status": book.status,
            })

        messages.success(request, f"Progress updated for '{book.title}' (Page {book.current_page}/{book.page_count or '?'}).")
    
    # Return to referrer or book detail
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER")
    if next_url:
        return redirect(next_url)
    return redirect("book_detail", book_id=book.id)

@login_required
def toggle_book_status_view(request, book_id):
    """
    Quick status toggle from the list view cards.
    """
    book = get_object_or_404(BookEntry, id=book_id, user=request.user)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in [s[0] for s in BookStatus.choices]:
            book.status = new_status
            if new_status == BookStatus.COMPLETED:
                if not book.finish_date:
                    book.finish_date = timezone.now().date()
                if book.page_count and book.current_page < book.page_count:
                    book.current_page = book.page_count
            elif new_status == BookStatus.READING and not book.start_date:
                book.start_date = timezone.now().date()
            book.save()
            messages.success(request, f"Moved '{book.title}' to {book.get_status_display()}.")

    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER")
    if next_url:
        return redirect(next_url)
    return redirect("book_list")

@login_required
def delete_book_view(request, book_id):
    """
    Deletes a book entry from the user's tracker.
    """
    book = get_object_or_404(BookEntry, id=book_id, user=request.user)
    if request.method == "POST":
        title = book.title
        book.delete()
        messages.success(request, f"Removed '{title}' from your library.")
        return redirect("book_list")
    return redirect("book_detail", book_id=book.id)
