from core import context_thread

@context_thread
def order_thread(order, request):
    from Analytics.models import SalesFunnel, CustomerLifetimeValue,OrderAnalytics

    CustomerLifetimeValue.objects.update_clv(user=request.user,
                                             db_name=request.tenant_db)

    for item in order.items.all():

        try:
            SalesFunnel.objects.add_entry(
                user=request.user,
                product=item.product,
                stage='checkout',
                session_data={}
                )
        except :pass

    OrderAnalytics.objects.add_entry(order, request.tenant_db)
        
    from django.core.management import call_command
    call_command('init_cohort')