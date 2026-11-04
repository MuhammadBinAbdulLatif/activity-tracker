from django.urls import path
from . import views

urlpatterns = [
    path('', views.exercise_list, name='exercise_list'),
    path('create/', views.exercise_create, name='exercise_create'),
    path('<slug:slug>/', views.exercise_detail, name='exercise_detail'),
    path('<slug:slug>/log/', views.exercise_log_create, name='exercise_log_create'),
    path('logs/<int:pk>/delete/', views.exercise_log_delete, name='exercise_log_delete'),
]
