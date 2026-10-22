from django.urls import path
from products.views import ProductsGenericView

urlpatterns = [
    path('v1/',ProductsGenericView.as_view()),
]