from django.urls import path
from . import views

urlpatterns = [
    path("", views.comic_list_view, name="comic_list"),
    path("search/", views.search_comics_view, name="comic_search"),
    path("add/", views.add_comic_view, name="comic_add"),
    path("<int:id>/", views.comic_detail_view, name="comic_detail"),
    path("<int:id>/update-progress/", views.update_comic_progress_view, name="comic_update_progress"),
    path("<int:id>/update-details/", views.update_comic_details_view, name="comic_update_details"),
    path("<int:id>/delete/", views.delete_comic_view, name="comic_delete"),
]
