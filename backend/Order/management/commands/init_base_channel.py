from django.core.management.base import BaseCommand
from django.apps import apps

class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):

        SalesChannelModel = apps.get_model('Order.SalesChannel')

        try:
            chanell = SalesChannelModel.objects.get(id=1)
        except:
            chanell = SalesChannelModel.objects.create(
                name="online",
                description="""Канал онлайн продаж. Продажы происходят из интернет магазина""")

        if chanell.name != "online":
            chanell.name = "online"
            chanell.save()