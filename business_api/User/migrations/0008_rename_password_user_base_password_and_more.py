# Generated by Django 5.1.4 on 2025-01-06 17:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0007_alter_user_email_alter_user_reg_date'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='password',
            new_name='base_password',
        ),
        migrations.RemoveField(
            model_name='user',
            name='reg_date',
        ),
    ]
