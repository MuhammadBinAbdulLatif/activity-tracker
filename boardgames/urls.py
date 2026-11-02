from django.urls import path
from . import views

urlpatterns = [
    path("", views.boardgame_list, name="boardgame_list"),
    path("search/", views.search_boardgames, name="search_boardgames"),
    path("add/", views.add_boardgame, name="add_boardgame"),
    path("<int:pk>/", views.boardgame_detail, name="boardgame_detail"),
    path("<int:pk>/log-play/", views.log_play, name="log_play"),
    path("<int:pk>/update-details/", views.update_boardgame_details, name="update_boardgame_details"),
    path("<int:pk>/delete/", views.delete_boardgame, name="delete_boardgame"),
]
