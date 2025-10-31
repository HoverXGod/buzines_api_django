from core import context_thread

@context_thread
def order_item_thread(order_item):
    from Analytics.models import StockHistory, InventoryTurnover, OrderItemAnalytics

    OrderItemAnalytics.objects.create_analytics(order_item)

    # Обновляем историю запасов
    StockHistory.history.add_entry(
        product=order_item.product,
        quantity=order_item.quanity,
        change_type=StockHistory.ChangeType.SALE
    )
    
    # Обновляем аналитику оборачиваемости
    InventoryTurnover.objects.add_entry(order_item.product)
