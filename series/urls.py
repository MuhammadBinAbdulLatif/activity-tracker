from django.urls import path
from .views import (
    series_list_view,
    search_series_view,
    add_series_view,
    advance_episode_view,
    sync_series_metadata_view,
    series_detail_view,
    update_series_details_view,
    delete_series_view,
)

urlpatterns = [
    path('', series_list_view, name='series_list'),
    path('search/', search_series_view, name='series_search'),
    path('add/', add_series_view, name='series_add'),
    path('<int:series_id>/', series_detail_view, name='series_detail'),
    path('<int:series_id>/advance/', advance_episode_view, name='series_advance_episode'),
    path('<int:series_id>/sync/', sync_series_metadata_view, name='series_sync'),
    path('<int:series_id>/update-details/', update_series_details_view, name='series_update_details'),
    path('<int:series_id>/delete/', delete_series_view, name='series_delete'),
]
