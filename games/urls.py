from django.urls import path
from . import views

urlpatterns = [
    path("", views.game_list, name="game_list"),
    path("search/", views.search_games, name="search_games"),
    path("add/", views.add_game, name="add_game"),
    path("<int:pk>/", views.game_detail, name="game_detail"),
    path("<int:pk>/quick-update/", views.quick_update_game, name="quick_update_game"),
    path("<int:pk>/update-details/", views.update_game_details, name="update_game_details"),
    path("<int:pk>/delete/", views.delete_game, name="delete_game"),
]
