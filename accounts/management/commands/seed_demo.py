"""
python manage.py seed_demo

Crea datos de demostración realistas (México) para todas las fases.
Es idempotente: vuelve a ejecutarse sin duplicar registros.
"""
import datetime
import random
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

User = get_user_model()


# ── Helpers ───────────────────────────────────────────────────────────────────

def days_ago(n):
    return (timezone.now() - datetime.timedelta(days=n)).replace(
        hour=random.randint(9, 18), minute=random.choice([0, 15, 30, 45]), second=0, microsecond=0
    )

def days_from_now(n):
    return (timezone.now() + datetime.timedelta(days=n)).replace(
        hour=random.randint(9, 18), minute=random.choice([0, 15, 30, 45]), second=0, microsecond=0
    )

def date_ago(n):
    return datetime.date.today() - datetime.timedelta(days=n)

def date_from_now(n):
    return datetime.date.today() + datetime.timedelta(days=n)


class Command(BaseCommand):
    help = "Carga datos de demostración (México) para pruebas."

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("\n=== seed_demo ===\n"))

        # Run create_groups first to ensure roles exist
        call_command("create_groups", verbosity=0)

        self._seed_users()
        self._seed_catalogs()
        self._seed_inventory()
        self._seed_owners()
        self._seed_patients()
        self._seed_appointments()
        self._seed_consultations()
        self._seed_vaccinations()
        self._seed_prescriptions()
        self._seed_lab_results()

        self.stdout.write(self.style.SUCCESS("\nOK Base de datos poblada correctamente.\n"))
        self._print_credentials()

    # ── 1. Users ──────────────────────────────────────────────────────────────

    def _seed_users(self):
        self.stdout.write("  -> Usuarios...")

        USERS = [
            dict(username="dra.garcia",    password="Vet1234!",        first_name="María",        last_name="García López",      email="garcia@vetclinic.mx",    phone="5551234001", professional_license="CED-VET-112233", group="Veterinario"),
            dict(username="dr.hernandez",  password="Vet1234!",        first_name="Carlos",       last_name="Hernández Ramírez", email="hernandez@vetclinic.mx", phone="5551234002", professional_license="CED-VET-445566", group="Veterinario"),
            dict(username="asist.luna",    password="Asist1234!",      first_name="Sofía",        last_name="Luna Morales",      email="luna@vetclinic.mx",      phone="5551234003", group="Asistente Veterinario"),
            dict(username="recep.torres",  password="Recep1234!",      first_name="Roberto",      last_name="Torres Díaz",       email="torres@vetclinic.mx",    phone="5551234004", group="Recepcionista"),
            dict(username="cliente.mtz",   password="Cliente1234!",    first_name="Juan",         last_name="Martínez Soto",     email="juan.martinez@gmail.com",phone="5559871001", group="Propietario"),
        ]

        self.users = {}
        for data in USERS:
            group_name = data.pop("group")
            password   = data.pop("password")
            u, created = User.objects.update_or_create(
                username=data["username"], defaults=data
            )
            u.set_password(password)
            u.save()
            group = Group.objects.get(name=group_name)
            u.groups.set([group])
            self.users[u.username] = u

        # Keep reference to vets
        self.vet1 = self.users["dra.garcia"]
        self.vet2 = self.users["dr.hernandez"]
        self.asist = self.users["asist.luna"]

        self.stdout.write(f"     {len(USERS)} usuarios OK")

    # ── 2. Catalogs ───────────────────────────────────────────────────────────

    def _seed_catalogs(self):
        self.stdout.write("  -> Catálogos (especies, razas, vacunas, medicamentos, tipos de cita)...")

        from patients.models import Species, Breed
        from medical.models import Vaccine, Medication
        from appointments.models import AppointmentType

        # Species + Breeds
        SPECIES = {
            "Perro": ["Labrador Retriever", "Golden Retriever", "Bulldog Francés",
                      "Chihuahua", "Poodle", "Pastor Alemán", "Beagle", "Mestizo"],
            "Gato":  ["Persa", "Siamés", "Maine Coon", "Doméstico Pelo Corto",
                      "Ragdoll", "Bengalí", "Mestizo"],
            "Ave":   ["Loro Amazona", "Periquito Australiano", "Cacatúa Ninfa", "Canario"],
            "Conejo":["Holland Lop", "Mini Rex", "Belier"],
            "Reptil":["Iguana Verde", "Tortuga de Tierra"],
            "Otro":  ["Hámster Sirio", "Cobaya"],
        }
        self.species = {}
        self.breeds  = {}
        for sp_name, breed_names in SPECIES.items():
            sp, _ = Species.objects.get_or_create(name=sp_name)
            self.species[sp_name] = sp
            self.breeds[sp_name] = []
            for br_name in breed_names:
                br, _ = Breed.objects.get_or_create(name=br_name, species=sp)
                self.breeds[sp_name].append(br)

        # Vaccines
        VACCINES = [
            ("DA2PP (Múltiple)",    "Zoetis",        "Distemper, Adenovirus, Parvovirus, Parainfluenza", "Serie inicial 3 dosis, luego anual"),
            ("Antirrábica",        "Merial",         "Rabia viral",                                      "Anual obligatoria"),
            ("Bordetella",         "Merck",          "Tos de las perreras",                              "Cada 6-12 meses"),
            ("Triple Felina (HHC)","Pfizer Animal",  "Panleucopenia, Herpesvirus, Calicivirus",          "Serie inicial 3 dosis, luego anual"),
            ("Leucemia Felina",    "Boehringer",     "Leucemia viral felina (FeLV)",                     "Inicial 2 dosis, luego anual"),
            ("Leptospirosis",      "Bayer Animal",   "Leptospirosis canina",                             "Anual, especialmente en zona tropical"),
            ("Influenza Equina",   "Hipra",          "Influenza",                                        "Cada 6 meses en caballos"),
        ]
        self.vaccines = []
        for name, mfr, disease, schedule in VACCINES:
            v, _ = Vaccine.objects.get_or_create(
                name=name,
                defaults=dict(manufacturer=mfr, disease=disease, recommended_schedule=schedule),
            )
            self.vaccines.append(v)

        # Medications
        MEDS = [
            ("Amoxicilina 500 mg",    "Amoxicilina",    "Cápsula 500 mg"),
            ("Metronidazol 250 mg",   "Metronidazol",   "Comprimido 250 mg"),
            ("Prednisolona 5 mg",     "Prednisolona",   "Comprimido 5 mg"),
            ("Ivermectina 1%",        "Ivermectina",    "Solución inyectable 1 %"),
            ("Meloxicam 1.5 mg/mL",   "Meloxicam",      "Solución oral 1.5 mg/mL"),
            ("Enrofloxacina 50 mg",   "Enrofloxacina",  "Comprimido 50 mg"),
            ("Tramadol 50 mg",        "Tramadol",       "Cápsula 50 mg"),
            ("Omeprazol 20 mg",       "Omeprazol",      "Cápsula 20 mg"),
            ("Furosemida 40 mg",      "Furosemida",     "Comprimido 40 mg"),
            ("Ketoconazol 200 mg",    "Ketoconazol",    "Comprimido 200 mg"),
            ("Cerenia 16 mg",         "Maropitant",     "Comprimido 16 mg (antiemético)"),
            ("Doxiciclina 100 mg",    "Doxiciclina",    "Cápsula 100 mg"),
        ]
        self.meds = []
        for name, active, presentation in MEDS:
            m, _ = Medication.objects.get_or_create(
                name=name,
                defaults=dict(active_ingredient=active, presentation=presentation),
            )
            self.meds.append(m)

        # Appointment types
        APPT_TYPES = [
            ("consultation", "Consulta General",    "#0d6efd", 30),
            ("vaccination",  "Vacunación",          "#198754", 20),
            ("surgery",      "Cirugía",             "#dc3545", 90),
            ("grooming",     "Estética / Baño",     "#6f42c1", 60),
            ("followup",     "Seguimiento",         "#fd7e14", 20),
            ("emergency",    "Urgencia",            "#d63384", 45),
        ]
        self.appt_types = {}
        for slug, label, color, duration in APPT_TYPES:
            at, _ = AppointmentType.objects.get_or_create(
                slug=slug,
                defaults=dict(label=label, color=color, default_duration=duration),
            )
            self.appt_types[slug] = at

        self.stdout.write("     Catálogos OK")

    # ── 3. Inventory ──────────────────────────────────────────────────────────

    def _seed_inventory(self):
        self.stdout.write("  -> Inventario...")
        from inventory.models import Product

        PRODUCTS = [
            # name,                      type,        unit,      stock, min_stock, lot,       exp
            ("DA2PP (Múltiple)",         "vaccine",   "dosis",   50,    10,       "LT-2024A", date_from_now(180)),
            ("Antirrábica",              "vaccine",   "dosis",   80,    15,       "LT-2024B", date_from_now(365)),
            ("Triple Felina (HHC)",      "vaccine",   "dosis",   40,    10,       "LT-2024C", date_from_now(200)),
            ("Leucemia Felina",          "vaccine",   "dosis",   25,    8,        "LT-2024D", date_from_now(150)),
            ("Amoxicilina 500 mg",       "medicine",  "cápsula", 200,   30,       "MED-001",  date_from_now(540)),
            ("Metronidazol 250 mg",      "medicine",  "comprimido",150, 20,       "MED-002",  date_from_now(480)),
            ("Prednisolona 5 mg",        "medicine",  "comprimido",100, 15,       "MED-003",  date_from_now(360)),
            ("Meloxicam 1.5 mg/mL",      "medicine",  "frasco",  30,    5,        "MED-004",  date_from_now(300)),
            ("Enrofloxacina 50 mg",      "medicine",  "comprimido",120, 20,       "MED-005",  date_from_now(400)),
            ("Tramadol 50 mg",           "medicine",  "cápsula", 80,    10,       "MED-006",  date_from_now(365)),
            ("Omeprazol 20 mg",          "medicine",  "cápsula", 60,    10,       "MED-007",  date_from_now(300)),
            ("Cerenia 16 mg",            "medicine",  "comprimido",40,  5,        "MED-008",  date_from_now(240)),
            ("Jeringas 5 mL",            "supply",    "pieza",   500,   50,       "",         None),
            ("Guantes nitrilo M",        "supply",    "par",     300,   50,       "",         None),
            ("Alcohol 96°",              "supply",    "litro",   20,    3,        "",         None),
            ("Gasas estériles 10x10",    "supply",    "pieza",   1000,  100,      "",         None),
            ("Bolsas de basura roja",    "supply",    "rollo",   4,     2,        "",         None),  # low stock alert
        ]

        for name, ptype, unit, stock, min_stock, lot, exp in PRODUCTS:
            Product.objects.get_or_create(
                name=name,
                defaults=dict(product_type=ptype, unit=unit, stock=stock,
                              min_stock=min_stock, lot=lot, expiration=exp),
            )
        self.stdout.write(f"     {len(PRODUCTS)} productos OK")

    # ── 4. Owners ─────────────────────────────────────────────────────────────

    def _seed_owners(self):
        self.stdout.write("  -> Propietarios...")
        from patients.models import Owner

        DATA = [
            ("Juan Martínez Soto",       "MASJ850312HDFRTJ05", "5559871001", "juan.martinez@gmail.com",     "Av. Insurgentes Sur 1602, Col. Crédito Constructor, CDMX",   "Ana Soto, 5559871099"),
            ("María Rodríguez Pérez",    "ROPM780514MDFDRJ08", "3312345678", "maria.rodriguez@hotmail.com", "Av. Vallarta 2300, Col. Arcos Vallarta, Guadalajara, Jal.",  "Pedro Rodríguez, 3312349999"),
            ("Carlos López Hernández",   "LOHC900228HNLLRC03", "8112233445", "carlos.lopez@outlook.com",    "Av. Constitución 501, Col. Centro, Monterrey, N.L.",         "Sara Hernández, 8112239000"),
            ("Ana González Morales",     "GOMA950610MDFLRN07", "5554567890", "ana.gonzalez@yahoo.com",      "Calle Morelos 45, Col. Del Valle, CDMX",                     "Luis González, 5554561234"),
            ("Roberto Sánchez García",   "SAGR881120HPLLRB02", "2224567890", "roberto.sanchez@gmail.com",   "Blvd. Hermanos Serdán 100, Col. Centro, Puebla, Pue.",       "Claudia García, 2224569999"),
            ("Sofía Flores Jiménez",     "FIJS920315MDFLRF06", "5556789012", "sofia.flores@gmail.com",      "Av. Revolución 1000, Col. Mixcoac, CDMX",                    "Marco Flores, 5556780000"),
            ("Diego Ramírez Castillo",   "RACD870704HBCMSG09", "6641234567", "diego.ramirez@hotmail.com",   "Av. Revolución 3000, Col. Zona Río, Tijuana, B.C.",          "Mónica Castillo, 6641239999"),
            ("Valentina Torres Cruz",    "TOCV001201MDFRVL04", "5553456789", "valentina.torres@gmail.com",  "Calle Durango 90, Col. Roma Norte, CDMX",                    "Enrique Torres, 5553450000"),
            ("Miguel Ángel Vargas Reyes","VARM830519HQRRGY01", "4421234567", "miguel.vargas@gmail.com",     "Av. Constituyentes 500, Col. Cimatario, Querétaro, Qro.",    "Daniela Reyes, 4421239999"),
            ("Lucía Moreno Álvarez",     "MOAL910723MDFRVC05", "5558901234", "lucia.moreno@outlook.com",    "Av. Coyoacán 1200, Col. Del Valle Centro, CDMX",             "Héctor Álvarez, 5558909999"),
        ]

        self.owners = []
        for full_name, id_doc, phone, email, address, emergency in DATA:
            o, _ = Owner.objects.get_or_create(
                email=email,
                defaults=dict(full_name=full_name, id_document=id_doc, phone=phone,
                              address=address, emergency_contact=emergency),
            )
            self.owners.append(o)
        self.stdout.write(f"     {len(self.owners)} propietarios OK")

    # ── 5. Patients ───────────────────────────────────────────────────────────

    def _seed_patients(self):
        self.stdout.write("  -> Pacientes...")
        from patients.models import Patient

        perro   = self.species["Perro"]
        gato    = self.species["Gato"]
        ave     = self.species["Ave"]
        conejo  = self.species["Conejo"]

        labrador  = self.breeds["Perro"][0]
        golden    = self.breeds["Perro"][1]
        bulldog   = self.breeds["Perro"][2]
        chihuahua = self.breeds["Perro"][3]
        poodle    = self.breeds["Perro"][4]
        pastor    = self.breeds["Perro"][5]
        mestizo_p = self.breeds["Perro"][7]
        persa     = self.breeds["Gato"][0]
        siames    = self.breeds["Gato"][1]
        domest    = self.breeds["Gato"][3]
        mestizo_g = self.breeds["Gato"][6]
        loro      = self.breeds["Ave"][0]
        periquito = self.breeds["Ave"][1]
        holandlop = self.breeds["Conejo"][0]

        # (name, species, breed, sex, dob_days_ago, weight, color, neutered, owner_idx, allergies, chronic, deceased)
        PATIENTS = [
            ("Rocky",    perro, labrador,  "M", 1095, 28.5, "Amarillo",     True,  0, "",                   "",                   False),
            ("Luna",     perro, golden,    "F", 730,  22.0, "Dorado",        True,  0, "",                   "",                   False),
            ("Mia",      gato,  persa,     "F", 1460, 3.8,  "Blanco",        True,  1, "Proteína de pollo",  "",                   False),
            ("Simón",    gato,  siames,    "M", 548,  4.2,  "Seal point",    False, 1, "",                   "",                   False),
            ("Max",      perro, bulldog,   "M", 912,  12.0, "Atigrado blanco",True, 2, "",                   "Brachicefalia",      False),
            ("Cleo",     perro, poodle,    "F", 365,  5.5,  "Blanco",        False, 2, "",                   "",                   False),
            ("Toby",     perro, pastor,    "M", 1825, 30.0, "Negro y café",  True,  3, "",                   "Displasia de cadera",False),
            ("Kira",     gato,  domest,    "F", 1095, 3.5,  "Naranja",       True,  3, "",                   "",                   False),
            ("Bruno",    perro, chihuahua, "M", 548,  2.8,  "Café",          False, 4, "",                   "",                   False),
            ("Nala",     gato,  mestizo_g, "F", 730,  3.2,  "Gris y blanco", True,  4, "",                   "",                   False),
            ("Zeus",     perro, labrador,  "M", 2190, 35.0, "Negro",         True,  5, "",                   "Hipotiroidismo",     False),
            ("Princesa", perro, mestizo_p, "F", 1460, 18.0, "Café oscuro",   True,  5, "",                   "",                   False),
            ("Paco",     ave,   loro,      "M", 3650, 0.4,  "Verde",         False, 6, "",                   "",                   False),
            ("Pipi",     ave,   periquito, "F", 365,  0.03, "Azul y blanco", False, 6, "",                   "",                   False),
            ("Oliver",   perro, golden,    "M", 730,  25.0, "Dorado",        True,  7, "",                   "",                   False),
            ("Canela",   gato,  domest,    "F", 912,  3.8,  "Atigrado café", True,  7, "",                   "",                   False),
            ("Bunny",    conejo,holandlop, "F", 365,  1.8,  "Blanco y gris", False, 8, "",                   "",                   False),
            ("Thor",     perro, pastor,    "M", 548,  22.0, "Negro y fuego", False, 9, "Sulfa",              "",                   False),
            ("Gorda",    gato,  mestizo_g, "F", 2555, 5.1,  "Blanco",        True,  9, "",                   "Enfermedad renal crónica",False),
        ]

        self.patients = []
        for (name, species, breed, sex, dob_days, weight,
             color, neutered, owner_idx, allergies, chronic, deceased) in PATIENTS:
            dob = date_ago(dob_days)
            p, _ = Patient.objects.get_or_create(
                name=name,
                owner=self.owners[owner_idx],
                defaults=dict(
                    species=species, breed=breed, sex=sex,
                    date_of_birth=dob, weight=weight, color=color,
                    neutered=neutered, allergies=allergies,
                    chronic_conditions=chronic, deceased=deceased,
                ),
            )
            self.patients.append(p)

        # Lineage: Luna es madre de Oliver, Rocky es padre de Oliver
        luna    = self.patients[1]   # Luna (golden female)
        rocky   = self.patients[0]   # Rocky (labrador male)
        oliver  = self.patients[14]  # Oliver (golden male)
        if not oliver.mother:
            oliver.mother = luna
        if not oliver.father:
            oliver.father = rocky
        oliver.save()

        self.stdout.write(f"     {len(self.patients)} pacientes OK (genealogia Rocky->Oliver<-Luna)")

    # ── 6. Appointments ───────────────────────────────────────────────────────

    def _seed_appointments(self):
        self.stdout.write("  -> Citas...")
        from appointments.models import Appointment

        cons  = self.appt_types["consultation"]
        vacc  = self.appt_types["vaccination"]
        surg  = self.appt_types["surgery"]
        groom = self.appt_types["grooming"]
        fup   = self.appt_types["followup"]
        emerg = self.appt_types["emergency"]

        v1, v2 = self.vet1, self.vet2

        # (patient_idx, vet, type, delta_days(negative=past), duration, status, reason)
        APPTS = [
            # ── Past completed ──────────────────────────────────────────────
            (0,  v1, cons,  -90, 30, "completed",  "Consulta de rutina anual"),
            (0,  v1, vacc,  -85, 20, "completed",  "Refuerzo DA2PP"),
            (1,  v1, cons,  -60, 30, "completed",  "Revisión piel y pelaje"),
            (2,  v2, cons,  -75, 30, "completed",  "Vómito crónico y pérdida de peso"),
            (2,  v2, vacc,  -70, 20, "completed",  "Triple felina"),
            (4,  v2, cons,  -45, 45, "completed",  "Dificultad respiratoria"),
            (5,  v1, vacc,  -30, 20, "completed",  "Primera dosis DA2PP"),
            (6,  v2, cons,  -50, 30, "completed",  "Revisión displasia cadera"),
            (9,  v1, cons,  -20, 30, "completed",  "Pérdida de apetito"),
            (10, v2, cons,  -40, 30, "completed",  "Control hipotiroidismo"),
            (14, v1, cons,  -15, 30, "completed",  "Primera consulta cachorro"),
            (17, v2, cons,  -10, 30, "completed",  "Prurito generalizado"),
            (3,  v2, surg,  -35, 90, "completed",  "Orquiectomía"),
            (11, v1, groom, -25, 60, "completed",  "Baño y corte"),
            # ── Cancelled ───────────────────────────────────────────────────
            (7,  v1, cons,  -5,  30, "cancelled",  "El propietario canceló"),
            (12, v2, cons,  -3,  30, "no_show",    "Revisión anual"),
            # ── Today / in-progress ─────────────────────────────────────────
            (1,  v1, vacc,   0,  20, "confirmed",  "Refuerzo anual antirrábica"),
            (8,  v2, cons,   0,  30, "in_progress","Tos persistente"),
            # ── Future ──────────────────────────────────────────────────────
            (0,  v1, fup,    3,  20, "scheduled",  "Seguimiento displasia cadera"),
            (2,  v2, vacc,   5,  20, "scheduled",  "Leucemia felina refuerzo"),
            (5,  v1, cons,   7,  30, "scheduled",  "Control de peso"),
            (13, v2, cons,  10,  30, "scheduled",  "Revisión plumas y comportamiento"),
            (15, v1, cons,  12,  30, "scheduled",  "Consulta nueva paciente"),
            (16, v2, cons,  14,  30, "scheduled",  "Control bienestar"),
            (4,  v2, surg,  20,  90, "confirmed",  "Extracción dental programada"),
            (6,  v1, cons,  21,  30, "scheduled",  "Revisión semestral"),
            (18, v2, emerg, 0,   45, "scheduled",  "Evaluación urgente por vómito"),
        ]

        self.appointments = {}
        for (pidx, vet, atype, delta, dur, status, reason) in APPTS:
            patient = self.patients[pidx]
            if delta <= 0:
                scheduled_at = days_ago(abs(delta))
            else:
                scheduled_at = days_from_now(delta)

            key = (pidx, atype.slug, delta)
            existing = Appointment.objects.filter(
                patient=patient, appointment_type=atype,
                scheduled_at__date=scheduled_at.date(),
            ).first()
            if not existing:
                existing = Appointment.objects.create(
                    patient=patient, vet=vet, appointment_type=atype,
                    scheduled_at=scheduled_at, duration=dur,
                    status=status, reason=reason,
                )
            self.appointments[key] = existing

        total = Appointment.objects.count()
        self.stdout.write(f"     {total} citas OK")

    # ── 7. Consultations ──────────────────────────────────────────────────────

    def _seed_consultations(self):
        self.stdout.write("  -> Consultas...")
        from appointments.models import Appointment
        from medical.models import Consultation, VitalsHistory

        DATA = [
            # (patient_idx, vet, date_days_ago, weight, temp, hr,
            #  anamnesis, physical_exam, diagnosis, treatment_plan, notes)
            (0, self.vet1, 90, 28.5, 38.4, 88,
             "Propietario refiere que el paciente se encuentra activo, come bien. Trae para revisión anual y actualización de vacunas.",
             "Mucosas rosadas y húmedas. Pulso regular y fuerte. Auscultación cardiopulmonar sin alteraciones. Abdomen blando, no doloroso. Piel y pelaje en buen estado.",
             "Paciente sano. Revisión anual sin hallazgos patológicos.",
             "Continuar dieta balanceada. Desparasitación interna con Ivermectina. Programar refuerzo vacunal DA2PP y antirrábica en 2 semanas.",
             ""),

            (1, self.vet1, 60, 22.0, 38.5, 90,
             "Dueña nota caída excesiva de pelo y piel seca desde hace 3 semanas. Paciente activo, come y bebe normal.",
             "BEG. MC rosadas. FC 90 lpm. FR 18 rpm. Alopecia leve en flancos. Piel seca con descamación fina. Sin prurito activo.",
             "Dermatitis seborreica leve secundaria a cambio de estación.",
             "Suplemento de ácidos grasos Omega-3 por 60 días. Baño semanal con shampoo hipoalergénico. Cita de seguimiento en 30 días.",
             "Recomendar humidificador en casa."),

            (2, self.vet2, 75, 3.5, 38.9, 160,
             "Propietaria reporta vómito 2-3 veces por semana, pérdida de peso progresiva en los últimos 2 meses. Apetito caprichoso.",
             "Paciente en condición corporal 2/5. MC pálidas. T° 38.9°C. FC 160 lpm. Abdomen ligeramente tenso. Pelaje opaco y seco.",
             "Síndrome de mala absorción. Descartar enfermedad inflamatoria intestinal vs. hipertiroidismo. Pendiente perfil bioquímico.",
             "Dieta hipoalergénica de hidrolizados proteicos. Metronidazol 10 mg/kg cada 12h por 10 días. Solicitar T4 y perfil completo.",
             "Alergia a proteína de pollo conocida – evitar alimentos con ave."),

            (4, self.vet2, 45, 11.5, 38.2, 105,
             "Dueño refiere mayor esfuerzo al respirar tras el ejercicio y ronquidos nocturnos desde hace 1 semana.",
             "Braquicéfalo con estenosis de narinas grado 2. Mucosas rosadas. Auscultación con estridor inspiratorio. SpO2 96%.",
             "Síndrome braquicefálico obstructivo. Estenosis de narinas grado 2.",
             "Reposo absoluto en ambiente fresco. Meloxicam 0.1 mg/kg cada 24h por 5 días. Evaluar corrección quirúrgica en consulta de seguimiento.",
             "Evitar ejercicio en horarios de calor. Informar riesgo anestésico elevado."),

            (6, self.vet2, 50, 29.8, 38.3, 76,
             "Propietario refiere que el paciente cojea del miembro posterior derecho desde cachorro. Se ha incrementado en los últimos 6 meses.",
             "Paciente en buen estado general. Cojera grado 3/5 en MPD. Crepitación articular leve en cadera derecha. Masa muscular glútea reducida.",
             "Displasia de cadera bilateral. Mayor afectación en hemicuerpo derecho. Rx confirmatorio.",
             "Meloxicam 0.1 mg/kg/día. Fisioterapia acuática 2 sesiones por semana. Suplemento de condroitín + glucosamina.",
             "Discutir con propietario opción de cirugía de reemplazo articular en futuro."),

            (9, self.vet1, 20, 3.0, 38.6, 150,
             "Propietaria nota que la gata no quiere comer desde hace 4 días. Bebe más agua de lo habitual.",
             "Paciente letárgica. CC 2/5. Mucosas ligeramente pálidas. T° 38.6°C. Riñones pequeños y firmes a la palpación. PD/PU.",
             "Sospecha de enfermedad renal crónica estadio 2 (IRIS). Confirmado con creatinina 2.8 mg/dL y BUN 48 mg/dL.",
             "Dieta renal comercial (Hill's k/d). Fluidoterapia subcutánea 100 mL diarios en casa. Control bioquímico en 30 días.",
             "Hipotiroidismo concurrente descartado (T4 normal)."),

            (10, self.vet2, 40, 34.2, 38.5, 82,
             "Control trimestral de hipotiroidismo. Propietario reporta mejor energía y menos caída de pelo desde el tratamiento.",
             "Paciente en BEG. CC 4/5. FC 82 lpm. Pelaje brillante. Sin mixedema. Peso estable.",
             "Hipotiroidismo canino en control. T4 total: 2.4 µg/dL (dentro de rango terapéutico).",
             "Continuar Levotiroxina 0.02 mg/kg cada 12h. Próximo control en 3 meses.",
             ""),

            (14, self.vet1, 15, 10.5, 38.7, 92,
             "Primera consulta. Cachorro de 6 meses adoptado hace 2 semanas. Sin vacunas previas documentadas.",
             "Cachorro activo y alerta. MC rosadas. Sin hallazgos patológicos. Dentición definitiva en erupción. BEG.",
             "Cachorro sano. Inicio de esquema de vacunación y desparasitación.",
             "DA2PP dosis 1 hoy. Recordar dosis 2 en 21 días y dosis 3 a los 30 días. Desparasitación con Ivermectina.",
             ""),

            (17, self.vet2, 10, 21.8, 39.1, 95,
             "Pastor alemán con prurito intenso en cara, patas y abdomen desde hace 2 semanas. Dueño reporta eritema y autotraumatismo.",
             "Eritema en región abdominal ventral, pata derecha y hocico. Excoriaciones por rascado. Prueba intradérmica positiva a pólenes ambientales.",
             "Dermatitis atópica canina moderada-severa. Posible reacción a ácaros del polvo.",
             "Prednisolona 1 mg/kg cada 24h por 7 días, luego reducción paulatina. Shampoo antiinflamatorio 2 veces por semana. Referir a dermatología.",
             "Alergias documentadas: sulfa. No usar trimetoprima-sulfa."),
        ]

        self.consultations = []
        for (pidx, vet, days, weight, temp, hr, anam, phys, diag, treat, notes) in DATA:
            patient = self.patients[pidx]
            c_date = date_ago(days)
            appt = Appointment.objects.filter(
                patient=patient, status="completed",
                scheduled_at__date__lte=c_date + datetime.timedelta(days=3),
                scheduled_at__date__gte=c_date - datetime.timedelta(days=3),
                consultation__isnull=True,
            ).first()

            c, created = Consultation.objects.get_or_create(
                patient=patient,
                date=c_date,
                defaults=dict(
                    appointment=appt, vet=vet,
                    anamnesis=anam, physical_exam=phys,
                    diagnosis=diag, treatment_plan=treat,
                    weight=weight, temperature=temp, heart_rate=hr,
                    notes=notes,
                ),
            )
            if created:
                VitalsHistory.objects.get_or_create(
                    patient=patient,
                    recorded_at=timezone.make_aware(datetime.datetime.combine(c_date, datetime.time(10, 0))),
                    defaults=dict(weight=weight, temperature=temp, heart_rate=hr),
                )
                if appt:
                    appt.status = "completed"
                    appt.save(update_fields=["status"])
            self.consultations.append(c)

        self.stdout.write(f"     {len(self.consultations)} consultas OK")

    # ── 8. Vaccinations ───────────────────────────────────────────────────────

    def _seed_vaccinations(self):
        self.stdout.write("  -> Vacunaciones...")
        from medical.models import VaccinationRecord

        da2pp   = self.vaccines[0]
        rabies  = self.vaccines[1]
        bord    = self.vaccines[2]
        triple  = self.vaccines[3]
        leuk    = self.vaccines[4]
        lepto   = self.vaccines[5]

        v1, v2 = self.vet1, self.vet2

        # (patient_idx, vaccine, applied_by, days_ago, lot, exp_days_from_now, next_due_days, site)
        VACC = [
            (0,  da2pp,  v1, 365, "LT-2024A", 180, 365,  "Subcutánea región interescapular"),
            (0,  rabies, v1, 360, "LT-2024B", 365, 360,  "Subcutánea región interescapular"),
            (0,  lepto,  v1, 355, "LT-2024E", 150, 355,  "Subcutánea región interescapular"),
            (1,  da2pp,  v1, 400, "LT-2024A", 180, 365,  "Subcutánea región interescapular"),
            (1,  rabies, v1, 395, "LT-2024B", 365, 370,  "Subcutánea región interescapular"),
            (2,  triple, v2, 370, "LT-2024C", 200, 370,  "Subcutánea región interescapular"),
            (2,  leuk,   v2, 360, "LT-2024D", 150, 360,  "Subcutánea región interescapular"),
            (3,  triple, v2, 180, "LT-2024C", 200, 185,  "Subcutánea región interescapular"),
            (4,  da2pp,  v2, 300, "LT-2024A", 180, 300,  "Subcutánea región interescapular"),
            (4,  rabies, v2, 295, "LT-2024B", 365, 295,  "Subcutánea región interescapular"),
            (5,  da2pp,  v1, 21,  "LT-2024A", 180, 21,   "Subcutánea región interescapular"),
            (6,  da2pp,  v2, 540, "LT-2023A", 10,  360,  "Subcutánea región interescapular"),   # vencida pronto
            (6,  rabies, v2, 535, "LT-2023B", 5,   350,  "Subcutánea región interescapular"),   # vencida
            (7,  triple, v1, 270, "LT-2024C", 200, 280,  "Subcutánea región interescapular"),
            (8,  da2pp,  v2, 180, "LT-2024A", 180, 185,  "Subcutánea región interescapular"),
            (10, da2pp,  v2, 300, "LT-2024A", 180, 310,  "Subcutánea región interescapular"),
            (10, rabies, v2, 295, "LT-2024B", 365, 295,  "Subcutánea región interescapular"),
            (14, da2pp,  v1, 15,  "LT-2024A", 180, None, "Subcutánea región interescapular"),   # primera dosis, sin próxima aún
            (17, da2pp,  v2, 180, "LT-2024A", 180, 185,  "Subcutánea región interescapular"),
            (18, triple, v2, 365, "LT-2024C", 200, 370,  "Subcutánea región interescapular"),
        ]

        count = 0
        for (pidx, vaccine, vet, days, lot, exp_days, next_days, site) in VACC:
            patient = self.patients[pidx]
            app_date = date_ago(days)
            exp_date = date_from_now(exp_days) if exp_days else None
            next_date = date_from_now(-next_days + days) if next_days else None

            VaccinationRecord.objects.get_or_create(
                patient=patient,
                vaccine=vaccine,
                application_date=app_date,
                defaults=dict(
                    lot=lot, expiration=exp_date, applied_by=vet,
                    next_due_date=next_date, application_site=site,
                ),
            )
            count += 1

        self.stdout.write(f"     {count} registros de vacunación OK")

    # ── 9. Prescriptions ──────────────────────────────────────────────────────

    def _seed_prescriptions(self):
        self.stdout.write("  -> Recetas...")
        from medical.models import Prescription, PrescriptionItem

        amox   = self.meds[0]
        metro  = self.meds[1]
        pred   = self.meds[2]
        melox  = self.meds[4]
        enro   = self.meds[5]
        trama  = self.meds[6]
        omep   = self.meds[7]
        ceren  = self.meds[10]
        doxy   = self.meds[11]

        # Each entry: (consultation_idx, issued_by, notes, [(med, dose, freq, dur, route, instr)])
        RX = [
            (0, self.vet1, "Administrar con alimento.",
             [(amox, "500 mg", "cada 12 h", "7 días", "oral", "Con alimento"),]),

            (2, self.vet2, "Dieta hipoalergénica estricta. Evitar proteína de pollo.",
             [(metro, "62.5 mg", "cada 12 h", "10 días", "oral", "Con alimento"),
              (omep,  "5 mg",   "cada 24 h", "14 días", "oral", "En ayunas 30 min antes"),]),

            (3, self.vet2, "Reposo. Evitar ejercicio en clima caluroso.",
             [(melox, "0.5 mg/kg", "cada 24 h", "5 días", "oral", "Con alimento"),]),

            (4, self.vet2, "Fisioterapia complementaria recomendada.",
             [(melox, "0.1 mg/kg", "cada 24 h", "30 días", "oral", "Con alimento"),]),

            (7, self.vet1, "Completar esquema vacunal en 21 días.",
             [(amox, "250 mg", "cada 12 h", "5 días", "oral", "Triturar en alimento"),]),

            (8, self.vet2, "Evitar sulfa y derivados. Control dermatológico en 3 semanas.",
             [(pred, "21 mg",  "cada 24 h", "7 días, luego reducir", "oral", "Con alimento"),
              (doxy, "100 mg", "cada 12 h", "10 días", "oral", "Con agua abundante"),]),
        ]

        count = 0
        for (cidx, vet, notes, items) in RX:
            if cidx >= len(self.consultations):
                continue
            consultation = self.consultations[cidx]
            rx, created = Prescription.objects.get_or_create(
                consultation=consultation,
                issued_by=vet,
                defaults=dict(notes=notes),
            )
            if created:
                for (med, dose, freq, dur, route, instr) in items:
                    PrescriptionItem.objects.create(
                        prescription=rx, medication=med,
                        dose=dose, frequency=freq, duration=dur,
                        route=route, instructions=instr,
                    )
                count += 1

        self.stdout.write(f"     {count} recetas nuevas OK")

    # ── 10. Lab Results ───────────────────────────────────────────────────────

    def _seed_lab_results(self):
        self.stdout.write("  -> Resultados de laboratorio...")
        from medical.models import LabResult

        DATA = [
            (2,  self.vet2, "Bioquímica sérica + T4 total",
             "Creatinina 0.8 mg/dL, BUN 22 mg/dL, ALT 55 U/L (levemente elevada), T4 3.2 µg/dL (normal). "
             "Glucosa 98 mg/dL. Proteínas totales 6.8 g/dL.", 72,
             "ALT levemente elevada, sin significado clínico relevante. Repetir en 6 meses."),

            (9,  self.vet1, "Perfil renal completo + UA",
             "Creatinina 2.8 mg/dL, BUN 48 mg/dL, Fósforo 5.9 mg/dL. "
             "Urianálisis: DU 1.010, proteínas +2, cilindros granulosos.", 18,
             "Compatible con ERC estadio IRIS 2. Iniciar tratamiento renal."),

            (10, self.vet2, "Perfil tiroideo canino",
             "T4 total: 2.4 µg/dL (rango terapéutico: 1.5-3.5 µg/dL). TSH canina: 0.08 ng/mL (normal <0.68).",
             38, "Paciente bien controlado. Mantener dosis actual de levotiroxina."),

            (4,  self.vet2, "Radiografía de tórax + hemograma",
             "Rx tórax: Tráquea desplazada, paladar blando elongado. Sin derrame pleural.\n"
             "Hemograma: Leucocitos 10,200/µL, Neutrófilos 72%, sin anemia.", 43,
             "Confirma síndrome braquicefálico. Cirugía correctiva planificada."),

            (6,  self.vet2, "Radiografía de cadera (ventro-dorsal)",
             "Cabezas femorales con aplanamiento bilateral. Acetábulos poco profundos. "
             "Score PennHIP: 0.62 derecho / 0.55 izquierdo. Artrosis incipiente.", 48,
             "Displasia severa bilateral. Candidato a cirugía de reemplazo articular."),
        ]

        count = 0
        for (pidx, vet, test, result, days, notes) in DATA:
            patient = self.patients[pidx]
            lr, created = LabResult.objects.get_or_create(
                patient=patient,
                test_name=test,
                date=date_ago(days),
                defaults=dict(result=result, ordered_by=vet, notes=notes),
            )
            if created:
                count += 1

        self.stdout.write(f"     {count} resultados de laboratorio OK")

    # ── Summary ───────────────────────────────────────────────────────────────

    def _print_credentials(self):
        self.stdout.write(self.style.MIGRATE_HEADING("\n=== CREDENCIALES DE ACCESO ===\n"))
        creds = [
            ("admin",          "Admin1234!",    "Superusuario / Admin"),
            ("dra.garcia",     "Vet1234!",      "Veterinaria — Dra. María García López"),
            ("dr.hernandez",   "Vet1234!",      "Veterinario — Dr. Carlos Hernández Ramírez"),
            ("asist.luna",     "Asist1234!",    "Asistente Veterinario — Sofía Luna Morales"),
            ("recep.torres",   "Recep1234!",    "Recepcionista — Roberto Torres Díaz"),
            ("cliente.mtz",    "Cliente1234!",  "Propietario — Juan Martínez Soto"),
        ]
        for username, password, role in creds:
            self.stdout.write(f"  {username:<18} {password:<16}  {role}")
        self.stdout.write("")
