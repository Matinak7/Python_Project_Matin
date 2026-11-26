from django.urls import path
from orders.views import OrderView, OrderDetailView, OrderCancelView





urlpatterns = [
    path('', OrderView.as_view(), name='orders'),

    path(
        '<int:order_id>/',
        OrderDetailView.as_view(),
        name='order_detail'
    ),

    path(
        '<int:order_id>/cancel/',
        OrderCancelView.as_view(),
        name='order_cancel'
    ),
]