from django.contrib.auth import get_user_model
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scraper_Api.settings")
django.setup()


User = get_user_model()

email = os.getenv("DJANGO_SUPERUSER_EMAIL")
password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

if not email or not password:
    print("❌ Lipsesc DJANGO_SUPERUSER_EMAIL sau DJANGO_SUPERUSER_PASSWORD în .env")
    exit(1)

if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(email=email, password=password)
    print(f"✅ Superuser creat: {email}")
else:
    print(f"ℹ️ Superuser deja existent: {email}")
