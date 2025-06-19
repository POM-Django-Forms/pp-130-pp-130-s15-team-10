from django.urls import path
from . import views


urlpatterns = [
    path('', views.show_books, name='show_books'),
    path('<int:book_id>/', views.book_detail, name='book_detail'),
    path('user_book/<int:user_id>/', views.user_detail_book, name='user_detail_book'),
    path('add/', views.add_book_view, name='add_book')
]
