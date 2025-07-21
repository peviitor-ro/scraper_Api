
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager
from company.models import Company
from scraper.models import Scraper

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("email address"), unique=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    company = models.ManyToManyField(Company, related_name='Companies', blank=True)
    scraper = models.ManyToManyField(Scraper, related_name='Scrapers', blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.is_superuser:
            self.company.set(Company.objects.values_list('id', flat=True))
            self.scraper.set(Scraper.objects.values_list('id', flat=True))
    