# Generated by Django 5.1.4 on 2025-03-23 11:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Product', '0004_grouppromotion'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='eta_title',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='meta_description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Product.category'),
        ),
        migrations.AddField(
            model_name='category',
            name='slug',
            field=models.SlugField(max_length=255, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='grouppromotion',
            name='end_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='grouppromotion',
            name='max_usage',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='grouppromotion',
            name='start_date',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='grouppromotion',
            name='used_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='personaldiscount',
            name='end_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='personaldiscount',
            name='max_usage',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='personaldiscount',
            name='start_date',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='personaldiscount',
            name='used_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='product',
            name='sku',
            field=models.CharField(max_length=32, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='product',
            name='slug',
            field=models.SlugField(max_length=255, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='product',
            name='stock',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='promotion',
            name='end_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='promotion',
            name='max_usage',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='promotion',
            name='start_date',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='promotion',
            name='used_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
