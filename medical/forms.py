import datetime
from django import forms
from django.forms import inlineformset_factory

from .models import Consultation, VaccinationRecord, DewormingRecord, Prescription, PrescriptionItem, LabResult


class ConsultationForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = (
            "patient", "appointment", "vet", "date",
            "anamnesis", "physical_exam", "diagnosis", "treatment_plan",
            "weight", "temperature", "heart_rate", "notes",
        )
        widgets = {
            "patient": forms.Select(attrs={"class": "form-select"}),
            "appointment": forms.Select(attrs={"class": "form-select"}),
            "vet": forms.Select(attrs={"class": "form-select"}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "anamnesis": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "physical_exam": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "diagnosis": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "treatment_plan": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "weight": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "temperature": forms.NumberInput(attrs={"class": "form-control", "step": "0.1"}),
            "heart_rate": forms.NumberInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.fields["vet"].queryset = User.objects.filter(is_active=True).order_by("first_name")
        self.fields["appointment"].required = False
        self.fields["weight"].required = False
        self.fields["temperature"].required = False
        self.fields["heart_rate"].required = False
        if not self.instance.pk:
            self.fields["date"].initial = datetime.date.today()


class VaccinationRecordForm(forms.ModelForm):
    class Meta:
        model = VaccinationRecord
        fields = (
            "patient", "vaccine", "application_date",
            "lot", "expiration", "applied_by",
            "next_due_date", "application_site",
        )
        widgets = {
            "patient": forms.Select(attrs={"class": "form-select"}),
            "vaccine": forms.Select(attrs={"class": "form-select"}),
            "application_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "lot": forms.TextInput(attrs={"class": "form-control"}),
            "expiration": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "applied_by": forms.Select(attrs={"class": "form-select"}),
            "next_due_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "application_site": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.fields["applied_by"].queryset = User.objects.filter(is_active=True).order_by("first_name")
        self.fields["expiration"].required = False
        self.fields["next_due_date"].required = False
        self.fields["application_site"].required = False
        self.fields["lot"].required = False
        if not self.instance.pk:
            self.fields["application_date"].initial = datetime.date.today()


class DewormingRecordForm(forms.ModelForm):
    class Meta:
        model = DewormingRecord
        fields = ("patient", "dewormer", "date", "weight", "lot", "next_due_date", "applied_by")
        widgets = {
            "patient": forms.Select(attrs={"class": "form-select"}),
            "dewormer": forms.Select(attrs={"class": "form-select"}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "weight": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "lot": forms.TextInput(attrs={"class": "form-control"}),
            "next_due_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "applied_by": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.fields["applied_by"].queryset = User.objects.filter(is_active=True).order_by("first_name")
        self.fields["weight"].required = False
        self.fields["lot"].required = False
        self.fields["next_due_date"].required = False
        if not self.instance.pk:
            self.fields["date"].initial = datetime.date.today()


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ("consultation", "notes")
        widgets = {
            "consultation": forms.Select(attrs={"class": "form-select"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["notes"].required = False


class PrescriptionItemForm(forms.ModelForm):
    class Meta:
        model = PrescriptionItem
        fields = ("medication", "dose", "frequency", "duration", "route", "instructions")
        widgets = {
            "medication": forms.Select(attrs={"class": "form-select form-select-sm"}),
            "dose": forms.TextInput(attrs={"class": "form-control form-control-sm", "placeholder": "p. ej. 5 mg/kg"}),
            "frequency": forms.TextInput(attrs={"class": "form-control form-control-sm", "placeholder": "p. ej. cada 12 h"}),
            "duration": forms.TextInput(attrs={"class": "form-control form-control-sm", "placeholder": "p. ej. 7 días"}),
            "route": forms.Select(attrs={"class": "form-select form-select-sm"}),
            "instructions": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
        }


PrescriptionItemFormSet = inlineformset_factory(
    Prescription,
    PrescriptionItem,
    form=PrescriptionItemForm,
    extra=3,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


class LabResultForm(forms.ModelForm):
    class Meta:
        model = LabResult
        fields = ("patient", "test_name", "result", "attachment", "ordered_by", "date", "notes")
        widgets = {
            "patient": forms.Select(attrs={"class": "form-select"}),
            "test_name": forms.TextInput(attrs={"class": "form-control"}),
            "result": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "attachment": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "ordered_by": forms.Select(attrs={"class": "form-select"}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.fields["ordered_by"].queryset = User.objects.filter(is_active=True).order_by("first_name")
        self.fields["attachment"].required = False
        self.fields["notes"].required = False
        if not self.instance.pk:
            self.fields["date"].initial = datetime.date.today()
