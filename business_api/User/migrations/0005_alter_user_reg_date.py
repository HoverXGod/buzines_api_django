# Generated by Django 5.1.4 on 2025-01-06 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0004_alter_user_reg_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='reg_date',
            field=models.DateField(),
        ),
    ]
