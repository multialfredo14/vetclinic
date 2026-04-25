from django.contrib import admin
from .models import AppointmentType, Appointment


@admin.register(AppointmentType)
class AppointmentTypeAdmin(admin.ModelAdmin):
    list_display = ("label", "slug", "default_duration", "color")
    search_fields = ("label",)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("patient", "vet", "appointment_type", "scheduled_at", "duration", "status")
    list_filter = ("status", "appointment_type", "scheduled_at")
    search_fields = ("patient__name", "vet__username", "vet__first_name", "reason")
    autocomplete_fields = ("patient", "vet")
    date_hierarchy = "scheduled_at"
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Cita", {"fields": ("patient", "vet", "appointment_type", "scheduled_at", "duration", "status")}),
        ("Detalle", {"fields": ("reason", "notes")}),
        ("Metadatos", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
