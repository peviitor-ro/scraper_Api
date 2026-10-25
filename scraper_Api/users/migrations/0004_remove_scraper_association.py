from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_customuser_scraper"),
    ]

    operations = [
        migrations.RunSQL(
            "DROP TABLE IF EXISTS users_customuser_scraper",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            "DROP TABLE IF EXISTS scraper_scraper",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
