from django.db import models
from django.conf import settings


class AppointmentType(models.Model):
    SLUG_CHOICES = [
        ("consultation", "Consulta"),
        ("vaccination", "Vacunación"),
        ("surgery", "Cirugía"),
        ("grooming", "Estética"),
        ("followup", "Seguimiento"),
        ("emergency", "Emergencia"),
    ]
    slug = models.CharField(max_length=20, choices=SLUG_CHOICES, unique=True, verbose_name="Clave")
    label = models.CharField(max_length=50, verbose_name="Etiqueta")
    color = models.CharField(max_length=7, default="#0d6efd", verbose_name="Color (hex)")
    default_duration = models.PositiveIntegerField(default=30, verbose_name="Duración predeterminada (min)")

    class Meta:
        verbose_name = "Tipo de cita"
        verbose_name_plural = "Tipos de cita"

    def __str__(self):
        return self.label


class Appointment(models.Model):
    STATUS_CHOICES = [
        ("scheduled", "Programada"),
        ("confirmed", "Confirmada"),
        ("in_progress", "En curso"),
        ("completed", "Completada"),
        ("cancelled", "Cancelada"),
        ("no_show", "No se presentó"),
    ]

    patient = models.ForeignKey(
        "patients.Patient", on_delete=models.CASCADE,
        related_name="appointments", verbose_name="Paciente",
    )
    vet = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="appointments", verbose_name="Veterinario",
    )
    appointment_type = models.ForeignKey(
        AppointmentType, on_delete=models.PROTECT, verbose_name="Tipo",
    )
    scheduled_at = models.DateTimeField(verbose_name="Fecha y hora")
    duration = models.PositiveIntegerField(default=30, verbose_name="Duración (min)")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="scheduled", verbose_name="Estado")
    reason = models.CharField(max_length=255, blank=True, verbose_name="Motivo de consulta")
    notes = models.TextField(blank=True, verbose_name="Notas")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cita"
        verbose_name_plural = "Citas"
        ordering = ["-scheduled_at"]

    def __str__(self):
        return f"{self.patient} — {self.scheduled_at:%d/%m/%Y %H:%M}"
