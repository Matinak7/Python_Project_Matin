from django.db import transaction
from products.models import Products
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from carts.models import Cart
from orders.models import Order, OrderItem
from orders.serializers import OrderSerializer







class OrderView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        orders = Order.objects.filter(
            user=request.user
        ).prefetch_related('items').order_by('-created_at')

        serializer = OrderSerializer(orders, many=True)

        return Response(serializer.data)

    def post(self, request):

        with transaction.atomic():

            cart = get_object_or_404(
                Cart.objects.select_for_update(),
                user=request.user
            )

            cart_items = list(
                cart.items.select_related('product').all()
            )

            if not cart_items:
                return Response(
                    {'error': 'Your cart is empty'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            total_price = 0
            order_products = []

            for item in cart_items:

                if item.quantity <= 0:
                    return Response(
                        {'error': 'Invalid product quantity'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                product = Products.objects.select_for_update().get(
                    pk=item.product_id
                )

                if product.count < item.quantity:
                    return Response(
                        {
                            'error': f'Not enough stock for {product.name}'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                total_price += product.price * item.quantity

                order_products.append((item, product))

            order = Order.objects.create(
                user=request.user,
                total_price=total_price
            )

            for item, product in order_products:

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    price=product.price,
                    quantity=item.quantity
                )

                product.count -= item.quantity

                product.save(update_fields=['count'])

            cart.items.all().delete()

            serializer = OrderSerializer(order)

            return Response(
                {
                    'message': 'Order created successfully',
                    'order': serializer.data
                },
                status=status.HTTP_201_CREATED
            )


class OrderDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):

        order = get_object_or_404(
            Order.objects.prefetch_related('items'),
            id=order_id,
            user=request.user
        )

        serializer = OrderSerializer(order)

        return Response(serializer.data)
