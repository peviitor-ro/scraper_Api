# Generated by Django 4.2.1 on 2023-06-07 23:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Api", "0002_testlogs_is_success_alter_testlogs_test_result"),
    ]

    operations = [
        migrations.AlterField(
            model_name="testlogs",
            name="is_success",
            field=models.CharField(max_length=10),
        ),
    ]
