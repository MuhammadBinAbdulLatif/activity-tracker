from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .services import get_real_dashboard_data

@login_required
def home_dashboard_view(request):
    """
    Renders the live uTrack home dashboard with real user data aggregated
    from Movies, Series, Books, Audiobooks, Comics, Games, Boardgames, and Exercises.
    """
    context = get_real_dashboard_data(user=request.user)
    return render(request, "dashboard/home.html", context)
