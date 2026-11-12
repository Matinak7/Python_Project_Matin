from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from carts.models import Cart, CartItem
from carts.serializers import CartSerializer
from products.models import Products


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, created = Cart.objects.get_or_create(
            user=request.user
        )

        serializer = CartSerializer(cart)

        return Response(serializer.data)


class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return Response(
                {'error': 'Invalid quantity'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if quantity < 1:
            return Response(
                {'error': 'Quantity must be greater than zero'},
                status=status.HTTP_400_BAD_REQUEST
            )

        product = get_object_or_404(
            Products,
            id=product_id
        )

        if product.count < quantity:
            return Response(
                {'error': 'Not enough product stock'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart, created = Cart.objects.get_or_create(
            user=request.user
        )

        item = CartItem.objects.filter(
            cart=cart,
            product=product
        ).first()

        if item:
            if item.quantity + quantity > product.count:
                return Response(
                    {'error': 'Not enough product stock'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            item.quantity += quantity
            item.save()

        else:
            CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=quantity
            )

        return Response(
            {'message': 'Product added successfully'},
            status=status.HTTP_201_CREATED
        )


class UpdateCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, item_id):

        cart = get_object_or_404(
            Cart,
            user=request.user
        )

        item = get_object_or_404(
            CartItem,
            id=item_id,
            cart=cart
        )

        try:
            quantity = int(request.data.get('quantity'))
        except (TypeError, ValueError):
            return Response(
                {'error': 'Invalid quantity'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if quantity < 1:
            return Response(
                {'error': 'Invalid quantity'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if quantity > item.product.count:
            return Response(
                {'error': 'Not enough stock'},
                status=status.HTTP_400_BAD_REQUEST
            )

        item.quantity = quantity
        item.save()

        return Response(
            {'message': 'Cart updated successfully'}
        )


class RemoveCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):

        cart = get_object_or_404(
            Cart,
            user=request.user
        )

        item = get_object_or_404(
            CartItem,
            id=item_id,
            cart=cart
        )

        item.delete()

        return Response(
            {'message': 'Product removed successfully'}
        )
