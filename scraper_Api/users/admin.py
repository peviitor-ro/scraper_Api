from django.contrib import admin
from .models import CustomUser
from .forms import CustomUserCreationForm


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserCreationForm

    search_fields = ["email", "company__company"]
    list_display = ["email", "is_active", "is_staff",
                    "is_superuser", "last_login", "date_joined"]
    list_filter = ["is_active", "is_staff", "is_superuser"]
    ordering = ["email"]
    readonly_fields = ["last_login", "date_joined"]
    list_editable = ["is_active", "is_staff", "is_superuser"]

    # Afișează câmpurile în formularul admin
    fields = ["email", "company", "scraper", "is_active",
              "is_staff", "is_superuser", "last_login", "date_joined"]
