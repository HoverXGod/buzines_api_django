# Generated by Django 5.1.4 on 2025-04-01 20:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0014_remove_user_addresss_user_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='acquisition_source',
            field=models.CharField(default='unknown', max_length=64),
        ),
    ]
