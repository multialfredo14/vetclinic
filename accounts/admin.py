from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "get_full_name", "email", "phone", "is_staff", "is_active")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("username", "first_name", "last_name", "email", "phone")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Datos de contacto", {"fields": ("phone", "address")}),
        ("Datos profesionales", {"fields": ("professional_license",)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Datos de contacto", {"fields": ("first_name", "last_name", "email", "phone", "address", "professional_license")}),
    )
