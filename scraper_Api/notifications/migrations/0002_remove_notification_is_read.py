# Generated by Django 4.2.9 on 2024-12-26 08:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="notification",
            name="is_read",
        ),
    ]