from django.urls import path
from .views import (
    series_list_view,
    search_series_view,
    add_series_view,
    advance_episode_view,
    sync_series_metadata_view,
)

urlpatterns = [
    path('', series_list_view, name='series_list'),
    path('search/', search_series_view, name='series_search'),
    path('add/', add_series_view, name='series_add'),
    path('<int:series_id>/advance/', advance_episode_view, name='series_advance_episode'),
    path('<int:series_id>/sync/', sync_series_metadata_view, name='series_sync'),
]
