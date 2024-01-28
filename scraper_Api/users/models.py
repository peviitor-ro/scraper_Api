
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager
from validator.models import Company
import random
import string

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("email address"), unique=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    secret = models.CharField(max_length=10)
    company = models.ManyToManyField(Company, related_name='Companies', blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        self.secret = self.generate_random_string(10)
        if self.is_superuser:
            # add all companies to superuser
            self.company.set(Company.objects.all())
        super(CustomUser, self).save(*args, **kwargs)
    
    def generate_random_string(self, length):
        letters = string.ascii_letters + string.digits
        return ''.join(random.choice(letters) for _ in range(length))