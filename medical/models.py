from django.db import models
from django.conf import settings
from simple_history.models import HistoricalRecords


class Consultation(models.Model):
    appointment = models.OneToOneField(
        "appointments.Appointment", on_delete=models.PROTECT,
        null=True, blank=True, related_name="consultation", verbose_name="Cita",
    )
    patient = models.ForeignKey(
        "patients.Patient", on_delete=models.CASCADE,
        related_name="consultations", verbose_name="Paciente",
    )
    vet = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name="Veterinario",
    )
    date = models.DateField(verbose_name="Fecha")
    anamnesis = models.TextField(verbose_name="Anamnesis")
    physical_exam = models.TextField(verbose_name="Exploración física")
    diagnosis = models.TextField(verbose_name="Diagnóstico")
    treatment_plan = models.TextField(verbose_name="Plan de tratamiento")
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Peso (kg)")
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, verbose_name="Temperatura (°C)")
    heart_rate = models.PositiveIntegerField(null=True, blank=True, verbose_name="Frecuencia cardíaca (lpm)")
    notes = models.TextField(blank=True, verbose_name="Notas adicionales")
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Consulta"
        verbose_name_plural = "Consultas"
        ordering = ["-date"]

    def __str__(self):
        return f"Consulta — {self.patient} ({self.date:%d/%m/%Y})"


class Vaccine(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre")
    manufacturer = models.CharField(max_length=100, blank=True, verbose_name="Laboratorio")
    disease = models.CharField(max_length=150, verbose_name="Enfermedad que previene")
    recommended_schedule = models.TextField(blank=True, verbose_name="Esquema recomendado")

    class Meta:
        verbose_name = "Vacuna (catálogo)"
        verbose_name_plural = "Vacunas (catálogo)"
        ordering = ["name"]

    def __str__(self):
        return self.name


class VaccinationRecord(models.Model):
    patient = models.ForeignKey(
        "patients.Patient", on_delete=models.CASCADE,
        related_name="vaccinations", verbose_name="Paciente",
    )
    vaccine = models.ForeignKey(Vaccine, on_delete=models.PROTECT, verbose_name="Vacuna")
    application_date = models.DateField(verbose_name="Fecha de aplicación")
    lot = models.CharField(max_length=50, blank=True, verbose_name="Lote")
    expiration = models.DateField(null=True, blank=True, verbose_name="Caducidad del lote")
    applied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name="Aplicado por",
    )
    next_due_date = models.DateField(null=True, blank=True, verbose_name="Próxima dosis")
    application_site = models.CharField(max_length=100, blank=True, verbose_name="Sitio de aplicación")
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Registro de vacunación"
        verbose_name_plural = "Registros de vacunación"
        ordering = ["-application_date"]

    def __str__(self):
        return f"{self.vaccine} — {self.patient} ({self.application_date:%d/%m/%Y})"


class Medication(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre")
    active_ingredient = models.CharField(max_length=150, blank=True, verbose_name="Principio activo")
    presentation = models.CharField(max_length=100, blank=True, verbose_name="Presentación")
    notes = models.TextField(blank=True, verbose_name="Notas")

    class Meta:
        verbose_name = "Medicamento (catálogo)"
        verbose_name_plural = "Medicamentos (catálogo)"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Prescription(models.Model):
    consultation = models.ForeignKey(
        Consultation, on_delete=models.CASCADE,
        related_name="prescriptions", verbose_name="Consulta",
    )
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name="Emitido por",
    )
    issued_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, verbose_name="Indicaciones generales")
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Receta"
        verbose_name_plural = "Recetas"
        ordering = ["-issued_at"]

    def __str__(self):
        return f"Receta #{self.pk} — {self.consultation.patient}"


class PrescriptionItem(models.Model):
    ROUTE_CHOICES = [
        ("oral", "Oral"),
        ("topical", "Tópica"),
        ("iv", "Intravenosa"),
        ("im", "Intramuscular"),
        ("sc", "Subcutánea"),
        ("ophthalmic", "Oftálmica"),
        ("other", "Otra"),
    ]
    prescription = models.ForeignKey(
        Prescription, on_delete=models.CASCADE,
        related_name="items", verbose_name="Receta",
    )
    medication = models.ForeignKey(Medication, on_delete=models.PROTECT, verbose_name="Medicamento")
    dose = models.CharField(max_length=100, verbose_name="Dosis")
    frequency = models.CharField(max_length=100, verbose_name="Frecuencia")
    duration = models.CharField(max_length=100, verbose_name="Duración")
    route = models.CharField(max_length=15, choices=ROUTE_CHOICES, default="oral", verbose_name="Vía de administración")
    instructions = models.TextField(blank=True, verbose_name="Instrucciones adicionales")

    class Meta:
        verbose_name = "Ítem de receta"
        verbose_name_plural = "Ítems de receta"

    def __str__(self):
        return f"{self.medication} — {self.dose}"


class LabResult(models.Model):
    patient = models.ForeignKey(
        "patients.Patient", on_delete=models.CASCADE,
        related_name="lab_results", verbose_name="Paciente",
    )
    test_name = models.CharField(max_length=150, verbose_name="Nombre del estudio")
    result = models.TextField(verbose_name="Resultado / interpretación")
    attachment = models.FileField(upload_to="lab_results/", null=True, blank=True, verbose_name="Archivo adjunto")
    ordered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name="Ordenado por",
    )
    date = models.DateField(verbose_name="Fecha")
    notes = models.TextField(blank=True, verbose_name="Observaciones")
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Resultado de laboratorio"
        verbose_name_plural = "Resultados de laboratorio"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.test_name} — {self.patient} ({self.date:%d/%m/%Y})"


class VitalsHistory(models.Model):
    patient = models.ForeignKey(
        "patients.Patient", on_delete=models.CASCADE,
        related_name="vitals_history", verbose_name="Paciente",
    )
    recorded_at = models.DateTimeField(verbose_name="Fecha y hora")
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Peso (kg)")
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, verbose_name="Temperatura (°C)")
    heart_rate = models.PositiveIntegerField(null=True, blank=True, verbose_name="FC (lpm)")

    class Meta:
        verbose_name = "Signos vitales"
        verbose_name_plural = "Historial de signos vitales"
        ordering = ["-recorded_at"]

    def __str__(self):
        return f"{self.patient} — {self.recorded_at:%d/%m/%Y %H:%M}"
