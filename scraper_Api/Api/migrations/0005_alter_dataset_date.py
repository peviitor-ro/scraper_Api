# Generated by Django 4.2.1 on 2023-10-14 21:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Api", "0004_dataset"),
    ]

    operations = [
        migrations.AlterField(
            model_name="dataset",
            name="date",
            field=models.DateTimeField(),
        ),
    ]
