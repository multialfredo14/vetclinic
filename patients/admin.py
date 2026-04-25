from django.contrib import admin
from .models import Owner, Species, Breed, Patient


@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "email", "id_document", "created_at")
    search_fields = ("full_name", "phone", "email", "id_document")
    list_filter = ("created_at",)


class BreedInline(admin.TabularInline):
    model = Breed
    extra = 1


@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    list_display = ("name",)
    inlines = [BreedInline]
    search_fields = ("name",)


@admin.register(Breed)
class BreedAdmin(admin.ModelAdmin):
    list_display = ("name", "species")
    list_filter = ("species",)
    search_fields = ("name",)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "species", "breed", "sex", "date_of_birth", "neutered", "deceased")
    list_filter = ("species", "sex", "neutered", "deceased", "created_at")
    search_fields = ("name", "owner__full_name", "microchip_id")
    autocomplete_fields = ("owner", "species", "breed", "mother", "father")
    readonly_fields = ("created_at",)
    fieldsets = (
        ("Identificación", {"fields": ("name", "owner", "photo", "microchip_id")}),
        ("Clasificación", {"fields": ("species", "breed", "sex", "color")}),
        ("Datos clínicos", {"fields": ("date_of_birth", "weight", "neutered", "allergies", "chronic_conditions")}),
        ("Genealogía", {"fields": ("mother", "father")}),
        ("Estado", {"fields": ("deceased", "date_of_death")}),
        ("Metadatos", {"fields": ("created_at",), "classes": ("collapse",)}),
    )
