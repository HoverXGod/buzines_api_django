
def process_order_item(order_item):
    from .models import StockHistory, InventoryTurnover

    # Обновляем историю запасов
    StockHistory.history.add_entry(
        product=order_item.product,
        quantity=order_item.quanity,
        change_type=StockHistory.ChangeType.SALE
    )
    
    # Обновляем аналитику оборачиваемости
    InventoryTurnover.objects.add_entry(order_item.product)
