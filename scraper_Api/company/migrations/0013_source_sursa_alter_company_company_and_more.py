# Generated by Django 4.2.9 on 2025-03-31 12:48

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("company", "0012_alter_dataset_date"),
    ]

    operations = [
        migrations.CreateModel(
            name="Source",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("sursa", models.CharField(max_length=50, unique=True)),
                ("image", models.ImageField(blank=True, upload_to="images/")),
            ],
        ),
        migrations.CreateModel(
            name="Sursa",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("sursa", models.CharField(max_length=50, unique=True)),
                ("image", models.ImageField(blank=True, upload_to="images/")),
            ],
        ),
        migrations.AlterField(
            model_name="company",
            name="company",
            field=models.TextField(max_length=300),
        ),
        migrations.AlterField(
            model_name="dataset",
            name="date",
            field=models.DateField(
                default=datetime.datetime(2025, 3, 31, 12, 48, 8, 631370)
            ),
        ),
        migrations.AddField(
            model_name="company",
            name="source",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="company",
                to="company.source",
            ),
        ),
    ]
