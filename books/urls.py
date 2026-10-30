from django.urls import path
from . import views

urlpatterns = [
    path('', views.book_list_view, name='book_list'),
    path('search/', views.search_books_view, name='search_books'),
    path('add/', views.add_book_view, name='add_book'),
    path('<int:book_id>/', views.book_detail_view, name='book_detail'),
    path('<int:book_id>/update-details/', views.update_book_details_view, name='update_book_details'),
    path('<int:book_id>/update-progress/', views.update_book_progress_view, name='update_book_progress'),
    path('<int:book_id>/toggle-status/', views.toggle_book_status_view, name='toggle_book_status'),
    path('<int:book_id>/delete/', views.delete_book_view, name='delete_book'),
]
