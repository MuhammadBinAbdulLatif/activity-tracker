from django.urls import path
from .views import home_dashboard_view

urlpatterns = [
    path('', home_dashboard_view, name='home'),
]
