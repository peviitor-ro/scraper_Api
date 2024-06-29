from django.contrib import admin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    
    # create a search bar for the admin page
    search_fields = ["email", "company__company"]
    # create a list of fields to display
    list_display = ["email", "is_active", "is_staff", "is_superuser", "last_login", "date_joined"]
    # create a list of fields to filter
    list_filter = ["is_active", "is_staff", "is_superuser"]
    # create a list of fields to sort by
    ordering = ["email"]
    # create a list of fields to be read only
    readonly_fields = ["last_login", "date_joined"]
    # create a list of fields to be editable
    list_editable = ["is_active", "is_staff", "is_superuser"]
