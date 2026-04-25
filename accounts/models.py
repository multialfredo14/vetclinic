from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    professional_license = models.CharField(max_length=50, blank=True, help_text="Cédula profesional (veterinarios)")

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return self.get_full_name() or self.username

    # ── Role helpers ──────────────────────────────────────────────────────────

    @property
    def is_admin_user(self):
        return self.is_superuser or self.groups.filter(name="Admin").exists()

    @property
    def is_vet(self):
        return self.groups.filter(name="Veterinario").exists()

    @property
    def is_assistant(self):
        return self.groups.filter(name="Asistente Veterinario").exists()

    @property
    def is_receptionist(self):
        return self.groups.filter(name="Recepcionista").exists()

    @property
    def is_client(self):
        return self.groups.filter(name="Propietario").exists()

    @property
    def can_view_medical(self):
        return self.is_admin_user or self.is_vet or self.is_assistant

    @property
    def can_edit_medical(self):
        return self.is_admin_user or self.is_vet

    @property
    def role_label(self):
        if self.is_superuser:
            return "Superusuario"
        group = self.groups.first()
        return group.name if group else "Sin rol"
