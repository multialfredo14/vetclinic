from django.db import models


class Owner(models.Model):
    full_name = models.CharField(max_length=150, verbose_name="Nombre completo")
    id_document = models.CharField(max_length=20, blank=True, verbose_name="CURP / RFC")
    phone = models.CharField(max_length=20, verbose_name="Teléfono")
    email = models.EmailField(blank=True, verbose_name="Correo electrónico")
    address = models.TextField(blank=True, verbose_name="Dirección")
    emergency_contact = models.CharField(max_length=150, blank=True, verbose_name="Contacto de emergencia")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Propietario"
        verbose_name_plural = "Propietarios"
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name


class Species(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Especie")

    class Meta:
        verbose_name = "Especie"
        verbose_name_plural = "Especies"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Breed(models.Model):
    species = models.ForeignKey(Species, on_delete=models.CASCADE, related_name="breeds", verbose_name="Especie")
    name = models.CharField(max_length=100, verbose_name="Raza")

    class Meta:
        verbose_name = "Raza"
        verbose_name_plural = "Razas"
        ordering = ["name"]
        unique_together = ("species", "name")

    def __str__(self):
        return f"{self.name} ({self.species})"


class Patient(models.Model):
    SEX_CHOICES = [("M", "Macho"), ("F", "Hembra")]

    name = models.CharField(max_length=100, verbose_name="Nombre")
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name="patients", verbose_name="Propietario")
    species = models.ForeignKey(Species, on_delete=models.PROTECT, verbose_name="Especie")
    breed = models.ForeignKey(Breed, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Raza")
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, verbose_name="Sexo")
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Fecha de nacimiento")
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Peso actual (kg)")
    color = models.CharField(max_length=80, blank=True, verbose_name="Color / pelaje")
    microchip_id = models.CharField(max_length=50, blank=True, null=True, unique=True, verbose_name="Microchip")
    neutered = models.BooleanField(default=False, verbose_name="Esterilizado/a")
    photo = models.ImageField(upload_to="patients/photos/", null=True, blank=True, verbose_name="Foto")
    mother = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="maternal_offspring", verbose_name="Madre",
        limit_choices_to={"sex": "F"},
    )
    father = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="paternal_offspring", verbose_name="Padre",
        limit_choices_to={"sex": "M"},
    )
    allergies = models.TextField(blank=True, verbose_name="Alergias conocidas")
    chronic_conditions = models.TextField(blank=True, verbose_name="Condiciones crónicas")
    deceased = models.BooleanField(default=False, verbose_name="Fallecido")
    date_of_death = models.DateField(null=True, blank=True, verbose_name="Fecha de fallecimiento")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.owner})"

    def offspring(self):
        return Patient.objects.filter(
            models.Q(mother=self) | models.Q(father=self)
        ).distinct()
