# Generated by Django 5.1.4 on 2025-03-19 22:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Product', '0002_alter_promocode_options_alter_category_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='quanity',
            field=models.FloatField(default=1.0),
        ),
    ]
