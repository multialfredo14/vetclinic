from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import (
    Consultation, Vaccine, VaccinationRecord,
    Dewormer, DewormingRecord,
    Medication, Prescription, PrescriptionItem, LabResult, VitalsHistory,
)


class PrescriptionItemInline(admin.TabularInline):
    model = PrescriptionItem
    extra = 1
    autocomplete_fields = ("medication",)


@admin.register(Consultation)
class ConsultationAdmin(SimpleHistoryAdmin):
    list_display = ("patient", "vet", "date", "diagnosis")
    list_filter = ("date", "vet")
    search_fields = ("patient__name", "vet__username", "diagnosis")
    autocomplete_fields = ("patient", "vet", "appointment")
    readonly_fields = ("created_at",)
    date_hierarchy = "date"
    fieldsets = (
        ("Paciente y médico", {"fields": ("patient", "vet", "appointment", "date")}),
        ("Signos vitales", {"fields": ("weight", "temperature", "heart_rate")}),
        ("Consulta", {"fields": ("anamnesis", "physical_exam", "diagnosis", "treatment_plan", "notes")}),
        ("Metadatos", {"fields": ("created_at",), "classes": ("collapse",)}),
    )


@admin.register(Vaccine)
class VaccineAdmin(admin.ModelAdmin):
    list_display = ("name", "manufacturer", "disease")
    search_fields = ("name", "manufacturer", "disease")


@admin.register(VaccinationRecord)
class VaccinationRecordAdmin(SimpleHistoryAdmin):
    list_display = ("patient", "vaccine", "application_date", "lot", "next_due_date", "applied_by")
    list_filter = ("vaccine", "application_date")
    search_fields = ("patient__name", "vaccine__name", "lot")
    autocomplete_fields = ("patient", "vaccine", "applied_by")
    date_hierarchy = "application_date"


@admin.register(Dewormer)
class DewormerAdmin(admin.ModelAdmin):
    list_display = ("name", "manufacturer", "type")
    search_fields = ("name", "manufacturer")


@admin.register(DewormingRecord)
class DewormingRecordAdmin(SimpleHistoryAdmin):
    list_display = ("patient", "dewormer", "date", "weight", "lot", "next_due_date", "applied_by")
    list_filter = ("dewormer", "date")
    search_fields = ("patient__name", "dewormer__name", "lot")
    autocomplete_fields = ("patient", "dewormer", "applied_by")
    date_hierarchy = "date"


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ("name", "active_ingredient", "presentation")
    search_fields = ("name", "active_ingredient")


@admin.register(Prescription)
class PrescriptionAdmin(SimpleHistoryAdmin):
    list_display = ("pk", "consultation", "issued_by", "issued_at")
    list_filter = ("issued_at",)
    search_fields = ("consultation__patient__name", "issued_by__username")
    autocomplete_fields = ("issued_by",)
    inlines = [PrescriptionItemInline]
    readonly_fields = ("issued_at",)


@admin.register(LabResult)
class LabResultAdmin(SimpleHistoryAdmin):
    list_display = ("test_name", "patient", "date", "ordered_by")
    list_filter = ("date",)
    search_fields = ("test_name", "patient__name", "ordered_by__username")
    autocomplete_fields = ("patient", "ordered_by")
    date_hierarchy = "date"


@admin.register(VitalsHistory)
class VitalsHistoryAdmin(admin.ModelAdmin):
    list_display = ("patient", "recorded_at", "weight", "temperature", "heart_rate")
    list_filter = ("recorded_at",)
    search_fields = ("patient__name",)
    autocomplete_fields = ("patient",)
    date_hierarchy = "recorded_at"
