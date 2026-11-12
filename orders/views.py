from django.db import transaction
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
        ).order_by('-created_at')

        serializer = OrderSerializer(
            orders,
            many=True
        )

        return Response(serializer.data)

    def post(self, request):

        try:
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
                products = []

                for item in cart_items:

                    product = item.product.__class__.objects.select_for_update().get(
                        id=item.product.id
                    )

                    if item.quantity > product.count:
                        return Response(
                            {
                                'error': f'Not enough stock for {product.name}'
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    products.append((item, product))

                    total_price += product.price * item.quantity

                order = Order.objects.create(
                    user=request.user,
                    total_price=total_price
                )

                for item, product in products:

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

        except Cart.DoesNotExist:
            return Response(
                {'error': 'Cart not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    def get(self, request):

        orders = Order.objects.filter(
            user=request.user
        ).order_by('-created_at')

        serializer = OrderSerializer(
            orders,
            many=True
        )

        return Response(serializer.data)


class OrderDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):

        order = get_object_or_404(
            Order,
            id=order_id,
            user=request.user
        )

        serializer = OrderSerializer(order)

        return Response(serializer.data)