from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .demo_data import get_demo_dashboard_data

@login_required
def home_dashboard_view(request):
    """
    Renders the primary uTrack home dashboard with active pursuits,
    heatmap timeline, planned items, and retrospective highlights.
    """
    context = get_demo_dashboard_data(username=request.user.username)
    return render(request, "dashboard/home.html", context)
