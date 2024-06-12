from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    
    # create a search bar for the admin page
    search_fields = ["email"]
    # create a list of fields to display
    list_display = ["email", "is_active", "is_staff", "is_superuser", "last_login", "date_joined"]
    # create a list of fields to filter
    list_filter = ["is_active", "is_staff", "is_superuser"]
    # create a list of fields to sort by
    ordering = ["email"]
    # create a list of fields to be read only
    readonly_fields = ["last_login", "date_joined"]
    # create a list of fields to be excluded
    exclude = ["password"]
    # create a list of fields to be editable
    list_editable = ["is_active", "is_staff", "is_superuser"]
    # create a list of fields to be displayed in the detail view
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        qs = super().get_queryset(request)
        return qs.filter(is_superuser=False)