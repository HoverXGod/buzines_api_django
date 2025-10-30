from processors import context_thread
from context.Analytics import order_item_thread, order_thread
from context.Order import create_order_items_thread


@context_thread
def order_create(request, order, product_dict=None):

    create_order_items_thread(order, product_dict).join()

    for item in order.items.all():
        order_item_thread(item)

    order_thread(order, request)