from django.urls import path
from . import views

urlpatterns = [
    path('', views.audiobook_list_view, name='audiobook_list'),
    path('search/', views.search_audiobooks_view, name='audiobook_search'),
    path('add/', views.add_audiobook_view, name='audiobook_add'),
    path('<int:audiobook_id>/', views.audiobook_detail_view, name='audiobook_detail'),
    path('<int:audiobook_id>/update-details/', views.update_audiobook_details_view, name='audiobook_update_details'),
    path('<int:audiobook_id>/update-progress/', views.update_audiobook_progress_view, name='audiobook_update_progress'),
    path('<int:audiobook_id>/delete/', views.delete_audiobook_view, name='audiobook_delete'),
]
