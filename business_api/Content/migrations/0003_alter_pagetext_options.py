# Generated by Django 5.1.4 on 2025-01-12 11:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Content', '0002_pagetext'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pagetext',
            options={'verbose_name': 'Текст страницы', 'verbose_name_plural': 'Тексты страницы'},
        ),
    ]
