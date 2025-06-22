from django.urls import path
from . import views

urlpatterns = [
    path('orders/', views.all_orders, name='all_orders'),
    path('order/<int:id>/', views.show_order, name='show_order'),
    path('own_orders/', views.show_own_orders, name='own_orders'),
    path('create/', views.create_order, name='create_order'),
    path('orders/close/', views.close_orders, name='close_orders'),
    path('order/<int:id>/close/', views.close_order, name='close_order')
]