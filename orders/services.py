from django.db import transaction
from carts.models import Cart
from products.models import Products
from orders.models import Order, OrderItem





@transaction.atomic
def create_order(user):

    cart = Cart.objects.select_for_update().get(
        user=user
    )

    cart_items = list(
        cart.items.all()
    )

    if not cart_items:
        raise ValueError('Your cart is empty')

    total_price = 0
    order_products = []

    for item in cart_items:

        if item.quantity <= 0:
            raise ValueError('Invalid quantity')

        product = Products.objects.select_for_update().get(
            id=item.product_id
        )

        if product.count < item.quantity:
            raise ValueError(
                f'Not enough stock for {product.name}'
            )

        total_price += product.price * item.quantity

        order_products.append((item, product))

    order = Order.objects.create(
        user=user,
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

    return order


@transaction.atomic
def cancel_order(user, order_id):

    order = Order.objects.select_for_update().get(
        id=order_id,
        user=user
    )

    if order.status not in ('pending', 'processing'):
        raise ValueError('This order cannot be cancelled')

    for item in order.items.all():
        if item.product_id:
            product = Products.objects.select_for_update().get(
                id=item.product_id
            )
            product.count += item.quantity
            product.save(update_fields=['count'])

    order.status = 'cancelled'
    order.save(update_fields=['status'])

    return order