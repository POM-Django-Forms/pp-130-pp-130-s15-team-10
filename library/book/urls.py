from django.urls import path
from . import views

urlpatterns = [
    path('', views.show_books, name='show_books'),
    path('<int:book_id>/', views.book_detail, name='book_detail'),
    path('create/', views.create_or_update_book, name='create_book'),
    path('<int:book_id>/update/', views.create_or_update_book, name='update_book'),
    path('delete/', views.delete_book, name='delete_book')
]
