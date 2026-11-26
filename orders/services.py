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
