from processors import context_thread

@context_thread
def create_order_items_thread(order, product_dict):
    from Order.models import OrderItem

    for item in product_dict:
        OrderItem.objects.create(
            order = order,
            product = product_dict[item]['product'],
            quanity = product_dict[item]['quanity'],
            price = product_dict[item]['price'],
            discount = product_dict[item]['discount'],
            promotion_name = product_dict[item]['promotion'].name,
            promotion_type = product_dict[item]['promotion'].__class__
        )