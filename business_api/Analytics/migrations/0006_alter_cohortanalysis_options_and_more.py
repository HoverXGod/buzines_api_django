# Generated by Django 5.1.4 on 2025-03-31 21:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Analytics', '0005_remove_paymentanalysis_gateway_performance_and_more'),
        ('Product', '0008_alter_product_category'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cohortanalysis',
            options={'ordering': ['-cohort_date', 'retention_day'], 'verbose_name': 'Когортный анализ', 'verbose_name_plural': 'Когортный анализ'},
        ),
        migrations.AlterModelOptions(
            name='customerlifetimevalue',
            options={'verbose_name': 'Пожизненная ценность пользователей', 'verbose_name_plural': 'Пожизненная ценность пользователей'},
        ),
        migrations.AlterModelOptions(
            name='productperformance',
            options={'verbose_name': 'Анализ продуктов', 'verbose_name_plural': 'Анализ продуктов'},
        ),
        migrations.AlterModelOptions(
            name='salesfunnel',
            options={'verbose_name': 'Воронки продаж', 'verbose_name_plural': 'Воронки продаж'},
        ),
        migrations.AlterField(
            model_name='cohortanalysis',
            name='cohort_date',
            field=models.DateField(help_text='Дата формирования когорты'),
        ),
        migrations.AlterField(
            model_name='cohortanalysis',
            name='metrics',
            field=models.JSONField(default=dict, help_text="\n    {\n        'total_users': int,\n        'active_users': int,\n        'revenue': float,\n        'avg_order_value': float,\n        'orders_count': int,\n        'arppu': float\n    }"),
        ),
        migrations.AlterField(
            model_name='cohortanalysis',
            name='primary_category',
            field=models.ForeignKey(blank=True, help_text='Автоматически определяемая категория', null=True, on_delete=django.db.models.deletion.SET_NULL, to='Product.category'),
        ),
        migrations.AlterField(
            model_name='cohortanalysis',
            name='retention_day',
            field=models.PositiveIntegerField(help_text='День удержания'),
        ),
    ]
