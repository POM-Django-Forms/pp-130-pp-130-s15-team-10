from django.urls import path
from . import views


app_name = 'author'

urlpatterns = [
    path('author/create/', views.create_author, name='create_author'),
    path('authors/', views.show_authors, name='show_authors'),
    path('author/delete/', views.remove_author, name='remove_author'),
]
