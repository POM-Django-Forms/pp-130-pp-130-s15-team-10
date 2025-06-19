from django.urls import path
from . import views
from .views import UpdateOrderView

urlpatterns = [
    path('orders/', views.all_orders, name='all_orders'),
    path('own_orders/', views.show_own_orders, name='own_orders'),
    path('create/', views.create_order, name='create_order'),
    path('close/', views.close_order, name='close_order'),
    path('update/<int:order_id>/', UpdateOrderView.as_view(), name='update_order'),
]