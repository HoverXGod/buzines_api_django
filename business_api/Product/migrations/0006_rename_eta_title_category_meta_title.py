# Generated by Django 5.1.4 on 2025-03-23 11:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Product', '0005_category_eta_title_category_meta_description_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='eta_title',
            new_name='meta_title',
        ),
    ]
