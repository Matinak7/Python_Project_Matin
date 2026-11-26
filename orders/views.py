from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from orders.models import Order
from orders.serializers import OrderSerializer
from orders.services import create_order, cancel_order
from carts.models import Cart






class OrderView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        orders = Order.objects.filter(
            user=request.user
        ).prefetch_related('items').order_by('-created_at')

        serializer = OrderSerializer(orders, many=True)

        return Response(serializer.data)

    def post(self, request):

        try:
            order = create_order(request.user)

        except Cart.DoesNotExist:
            return Response(
                {'error': 'Cart not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

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


class OrderCancelView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):

        try:
            order = cancel_order(request.user, order_id)

        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            'message': 'Order cancelled successfully',
            'order': OrderSerializer(order).data
        })