# Generated by Django 5.1.4 on 2025-03-23 19:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Order', '0004_order_billing_address_order_notes_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='dilivery',
            new_name='delivery',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='dilivery_status',
            new_name='delivery_status',
        ),
    ]
