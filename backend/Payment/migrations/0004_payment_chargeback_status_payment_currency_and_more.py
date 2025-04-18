# Generated by Django 5.1.4 on 2025-03-23 22:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Payment', '0003_payment_processed_at_alter_payment_cost_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='chargeback_status',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='payment',
            name='currency',
            field=models.CharField(default='RUB', max_length=3),
        ),
        migrations.AddField(
            model_name='payment',
            name='fee',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='payment',
            name='risk_score',
            field=models.FloatField(null=True),
        ),
    ]
