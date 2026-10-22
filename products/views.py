from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.response import Response
from products.models import Products
from products.serializers import  ProductsSerializerV3
from rest_framework import generics


class ProductsGenericView(generics.ListAPIView):
    queryset = Products.objects.all()
    serializer_class = ProductsSerializerV3
