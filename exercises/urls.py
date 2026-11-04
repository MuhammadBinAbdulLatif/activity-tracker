from django.urls import path
from . import views

urlpatterns = [
    path('', views.exercise_list, name='exercise_list'),
    path('search-catalog/', views.search_catalog_modal, name='search_catalog_modal'),
    path('create/', views.exercise_create, name='exercise_create'),
    path('track/<int:exercise_id>/', views.track_exercise, name='track_exercise'),
    path('tracks/<int:track_id>/status/', views.update_track_status, name='update_track_status'),
    path('tracks/<int:track_id>/untrack/', views.untrack_exercise, name='untrack_exercise'),
    path('<slug:slug>/', views.exercise_detail, name='exercise_detail'),
    path('<slug:slug>/log/', views.exercise_log_create, name='exercise_log_create'),
    path('logs/<int:pk>/delete/', views.exercise_log_delete, name='exercise_log_delete'),
]
