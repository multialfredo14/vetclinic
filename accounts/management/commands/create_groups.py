from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand


GROUPS = {
    "Admin": {
        "patients": ["owner", "species", "breed", "patient"],
        "appointments": ["appointmenttype", "appointment"],
        "medical": ["consultation", "vaccine", "vaccinationrecord", "medication", "prescription", "prescriptionitem", "labresult", "vitalshistory"],
        "inventory": ["product", "stockmovement"],
        "accounts": ["user"],
    },
    "Veterinario": {
        "patients": ["owner", "species", "breed", "patient"],
        "appointments": ["appointmenttype", "appointment"],
        "medical": ["consultation", "vaccine", "vaccinationrecord", "medication", "prescription", "prescriptionitem", "labresult", "vitalshistory"],
    },
    "Asistente Veterinario": {
        "patients": ["patient"],
        "appointments": ["appointment"],
        "medical": ["vaccinationrecord", "vitalshistory", "labresult"],
    },
    "Recepcionista": {
        "patients": ["owner", "patient"],
        "appointments": ["appointment"],
    },
    "Propietario": {},
}

VIEW_ONLY = {"Asistente Veterinario", "Propietario"}


class Command(BaseCommand):
    help = "Crea los grupos de roles con sus permisos."

    def handle(self, *args, **options):
        for group_name, app_models in GROUPS.items():
            group, created = Group.objects.get_or_create(name=group_name)
            group.permissions.clear()
            view_only = group_name in VIEW_ONLY

            for app_label, model_names in app_models.items():
                for model_name in model_names:
                    try:
                        ct = ContentType.objects.get(app_label=app_label, model=model_name)
                    except ContentType.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f"  Modelo no encontrado: {app_label}.{model_name}"))
                        continue

                    codenames = [f"view_{model_name}"]
                    if not view_only:
                        codenames += [f"add_{model_name}", f"change_{model_name}", f"delete_{model_name}"]

                    for codename in codenames:
                        try:
                            perm = Permission.objects.get(content_type=ct, codename=codename)
                            group.permissions.add(perm)
                        except Permission.DoesNotExist:
                            pass

            status = "creado" if created else "actualizado"
            self.stdout.write(self.style.SUCCESS(f"  Grupo '{group_name}' {status}."))

        self.stdout.write(self.style.SUCCESS("OK Grupos configurados correctamente."))
