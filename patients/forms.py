from django import forms
from .models import Owner, Patient, Breed


class OwnerForm(forms.ModelForm):
    class Meta:
        model = Owner
        fields = ("full_name", "id_document", "phone", "email", "address", "emergency_contact")
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "id_document": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "emergency_contact": forms.TextInput(attrs={"class": "form-control"}),
        }


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = (
            "name", "owner", "species", "breed", "sex",
            "date_of_birth", "weight", "color", "microchip_id",
            "neutered", "photo", "mother", "father",
            "allergies", "chronic_conditions", "deceased", "date_of_death",
        )
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "owner": forms.Select(attrs={"class": "form-select"}),
            "species": forms.Select(attrs={"class": "form-select", "id": "id_species"}),
            "breed": forms.Select(attrs={"class": "form-select", "id": "id_breed"}),
            "sex": forms.Select(attrs={"class": "form-select"}),
            "date_of_birth": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "weight": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "color": forms.TextInput(attrs={"class": "form-control"}),
            "microchip_id": forms.TextInput(attrs={"class": "form-control"}),
            "photo": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "mother": forms.Select(attrs={"class": "form-select"}),
            "father": forms.Select(attrs={"class": "form-select"}),
            "allergies": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "chronic_conditions": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "date_of_death": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Resolve which species is active: saved instance > POST data > none
        species_id = None
        if self.instance.pk and self.instance.species_id:
            species_id = self.instance.species_id
        elif self.data.get("species"):
            try:
                species_id = int(self.data["species"])
            except (ValueError, TypeError):
                pass
        self.fields["breed"].queryset = (
            Breed.objects.filter(species_id=species_id) if species_id else Breed.objects.none()
        )
        self.fields["breed"].required = False
        self.fields["mother"].required = False
        self.fields["father"].required = False
        self.fields["date_of_death"].required = False
