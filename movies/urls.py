from django.urls import path
from .views import (
    movie_list_view,
    search_movies_view,
    add_movie_view,
    movie_detail_view,
    update_movie_details_view,
    update_movie_status_view,
    rewatch_movie_view,
    delete_movie_view,
)

urlpatterns = [
    path('', movie_list_view, name='movie_list'),
    path('search/', search_movies_view, name='movie_search'),
    path('add/', add_movie_view, name='movie_add'),
    path('<int:movie_id>/', movie_detail_view, name='movie_detail'),
    path('<int:movie_id>/update-details/', update_movie_details_view, name='movie_update_details'),
    path('<int:movie_id>/update-status/', update_movie_status_view, name='movie_update_status'),
    path('<int:movie_id>/rewatch/', rewatch_movie_view, name='movie_rewatch'),
    path('<int:movie_id>/delete/', delete_movie_view, name='movie_delete'),
]
