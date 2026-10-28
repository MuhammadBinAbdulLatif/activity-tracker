from django.urls import path
from .views import (
    movie_list_view,
    search_movies_view,
    add_movie_view,
    update_movie_status_view,
    rewatch_movie_view,
)

urlpatterns = [
    path('', movie_list_view, name='movie_list'),
    path('search/', search_movies_view, name='movie_search'),
    path('add/', add_movie_view, name='movie_add'),
    path('update/<int:movie_id>/', update_movie_status_view, name='movie_update_status'),
    path('rewatch/<int:movie_id>/', rewatch_movie_view, name='movie_rewatch'),
]
