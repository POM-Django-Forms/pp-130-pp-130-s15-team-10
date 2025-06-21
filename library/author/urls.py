from django.urls import path
from . import views

app_name = 'author'

urlpatterns = [
    path('author/create/', views.create_or_update_author, name='create_author'),
    path('author/<int:author_id>/update/', views.create_or_update_author, name='update_author'),
    path('authors/', views.show_authors, name='show_authors'),
    path('author/delete/', views.delete_author, name='delete_author'),
    path('author/<int:author_id>/', views.show_author, name='show_author')
]
