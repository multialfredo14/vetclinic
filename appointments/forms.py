from datetime import timedelta
from django import forms
from .models import AppointmentType, Appointment


class AppointmentTypeForm(forms.ModelForm):
    class Meta:
        model = AppointmentType
        fields = ("slug", "label", "color", "default_duration")
        widgets = {
            "slug": forms.Select(attrs={"class": "form-select"}),
            "label": forms.TextInput(attrs={"class": "form-control"}),
            "color": forms.TextInput(attrs={"class": "form-control", "type": "color"}),
            "default_duration": forms.NumberInput(attrs={"class": "form-control"}),
        }


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ("patient", "vet", "appointment_type", "scheduled_at", "duration", "reason", "notes")
        widgets = {
            "patient": forms.Select(attrs={"class": "form-select"}),
            "vet": forms.Select(attrs={"class": "form-select"}),
            "appointment_type": forms.Select(attrs={"class": "form-select"}),
            "scheduled_at": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "duration": forms.NumberInput(attrs={"class": "form-control"}),
            "reason": forms.TextInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.fields["vet"].queryset = User.objects.filter(is_active=True).order_by("first_name")
        if self.instance.pk and self.instance.scheduled_at:
            self.initial["scheduled_at"] = self.instance.scheduled_at.strftime("%Y-%m-%dT%H:%M")

    def clean(self):
        cleaned_data = super().clean()
        vet = cleaned_data.get("vet")
        scheduled_at = cleaned_data.get("scheduled_at")
        duration = cleaned_data.get("duration") or 30

        if vet and scheduled_at:
            end_time = scheduled_at + timedelta(minutes=duration)
            conflicts = Appointment.objects.filter(
                vet=vet,
                status__in=("scheduled", "confirmed", "in_progress"),
            )
            if self.instance.pk:
                conflicts = conflicts.exclude(pk=self.instance.pk)

            for appt in conflicts:
                appt_end = appt.scheduled_at + timedelta(minutes=appt.duration)
                if scheduled_at < appt_end and end_time > appt.scheduled_at:
                    raise forms.ValidationError(
                        f"Conflicto: el veterinario ya tiene cita de "
                        f"{appt.scheduled_at:%H:%M} a {appt_end:%H:%M} "
                        f"el {appt.scheduled_at:%d/%m/%Y}."
                    )
        return cleaned_data


class AppointmentStatusForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ("status", "notes")
        widgets = {
            "status": forms.Select(attrs={"class": "form-select"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
