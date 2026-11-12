from django.urls import path
from carts.views import (
    CartView,
    AddToCartView,
    UpdateCartItemView,
    RemoveCartItemView
)




urlpatterns = [
    path('', CartView.as_view(), name='cart'),
    path('add/', AddToCartView.as_view(), name='add_to_cart'),
    path('update/<int:item_id>/', UpdateCartItemView.as_view(), name='update_cart'),
    path('remove/<int:item_id>/', RemoveCartItemView.as_view(), name='remove_cart'),
]