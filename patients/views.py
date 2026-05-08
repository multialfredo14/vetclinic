from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from accounts.mixins import RoleRequiredMixin
from .forms import OwnerForm, PatientForm
from .models import Breed, Owner, Patient, Species


# ── Owners ────────────────────────────────────────────────────────────────────

class OwnerListView(LoginRequiredMixin, ListView):
    model = Owner
    template_name = "patients/owner_list.html"
    context_object_name = "owners"
    paginate_by = 20

    def get_queryset(self):
        qs = Owner.objects.prefetch_related("patients")
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(Q(full_name__icontains=q) | Q(phone__icontains=q) | Q(email__icontains=q))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["query"] = self.request.GET.get("q", "")
        return ctx


class OwnerDetailView(LoginRequiredMixin, DetailView):
    model = Owner
    template_name = "patients/owner_detail.html"
    context_object_name = "owner"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["patients"] = self.object.patients.select_related("species", "breed")
        return ctx


class OwnerCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = ["Admin", "Recepcionista", "Veterinario"]
    model = Owner
    form_class = OwnerForm
    template_name = "patients/owner_form.html"

    def get_success_url(self):
        messages.success(self.request, f"Propietario '{self.object.full_name}' creado.")
        return reverse_lazy("patients:owner_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Nuevo propietario"
        return ctx


class OwnerUpdateView(RoleRequiredMixin, UpdateView):
    allowed_roles = ["Admin", "Recepcionista", "Veterinario"]
    model = Owner
    form_class = OwnerForm
    template_name = "patients/owner_form.html"

    def get_success_url(self):
        messages.success(self.request, "Propietario actualizado.")
        return reverse_lazy("patients:owner_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = f"Editar: {self.object.full_name}"
        return ctx


class OwnerDeleteView(RoleRequiredMixin, DeleteView):
    allowed_roles = ["Admin"]
    model = Owner
    template_name = "patients/owner_confirm_delete.html"
    success_url = reverse_lazy("patients:owner_list")

    def form_valid(self, form):
        messages.success(self.request, f"Propietario '{self.object.full_name}' eliminado.")
        return super().form_valid(form)


# ── Patients ──────────────────────────────────────────────────────────────────

class PatientListView(LoginRequiredMixin, ListView):
    model = Patient
    template_name = "patients/patient_list.html"
    context_object_name = "patients"
    paginate_by = 20

    def get_queryset(self):
        qs = Patient.objects.select_related("owner", "species", "breed")
        q = self.request.GET.get("q", "").strip()
        species_id = self.request.GET.get("species", "")
        sex = self.request.GET.get("sex", "")
        if q:
            qs = qs.filter(
                Q(name__icontains=q) | Q(owner__full_name__icontains=q) | Q(microchip_id__icontains=q)
            )
        if species_id:
            qs = qs.filter(species_id=species_id)
        if sex:
            qs = qs.filter(sex=sex)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["query"] = self.request.GET.get("q", "")
        ctx["species_filter"] = self.request.GET.get("species", "")
        ctx["sex_filter"] = self.request.GET.get("sex", "")
        ctx["species_list"] = Species.objects.all()
        return ctx


class PatientDetailView(LoginRequiredMixin, DetailView):
    model = Patient
    template_name = "patients/patient_detail.html"
    context_object_name = "patient"

    def get_context_data(self, **kwargs):
        import datetime
        ctx = super().get_context_data(**kwargs)
        p = self.object
        ctx["offspring"] = p.offspring()
        ctx["recent_consultations"] = p.consultations.select_related("vet").order_by("-date")[:5]
        ctx["vaccinations"] = p.vaccinations.select_related("vaccine", "applied_by").order_by("-application_date")[:5]
        ctx["today"] = datetime.date.today()
        return ctx


class PatientCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = ["Admin", "Recepcionista", "Veterinario"]
    model = Patient
    form_class = PatientForm
    template_name = "patients/patient_form.html"

    def get_success_url(self):
        messages.success(self.request, f"Paciente '{self.object.name}' registrado.")
        return reverse_lazy("patients:patient_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Nuevo paciente"
        ctx["species_list"] = Species.objects.prefetch_related("breeds")
        return ctx


class PatientUpdateView(RoleRequiredMixin, UpdateView):
    allowed_roles = ["Admin", "Recepcionista", "Veterinario"]
    model = Patient
    form_class = PatientForm
    template_name = "patients/patient_form.html"

    def get_success_url(self):
        messages.success(self.request, "Paciente actualizado.")
        return reverse_lazy("patients:patient_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = f"Editar: {self.object.name}"
        ctx["species_list"] = Species.objects.prefetch_related("breeds")
        return ctx


class PatientDeleteView(RoleRequiredMixin, DeleteView):
    allowed_roles = ["Admin"]
    model = Patient
    template_name = "patients/patient_confirm_delete.html"
    success_url = reverse_lazy("patients:patient_list")

    def form_valid(self, form):
        messages.success(self.request, f"Paciente '{self.object.name}' eliminado.")
        return super().form_valid(form)


# ── Breed autocomplete (AJAX) ─────────────────────────────────────────────────

@login_required
def breeds_by_species(request):
    species_id = request.GET.get("species_id")
    breeds = Breed.objects.filter(species_id=species_id).values("id", "name") if species_id else []
    return JsonResponse({"breeds": list(breeds)})


@login_required
def patient_json(request, pk):
    patient = get_object_or_404(Patient.objects.select_related("owner", "species", "breed"), pk=pk)
    return JsonResponse({
        "name": patient.name,
        "species": patient.species.name,
        "breed": patient.breed.name if patient.breed else "",
        "sex": patient.get_sex_display(),
        "date_of_birth": patient.date_of_birth.strftime("%d/%m/%Y") if patient.date_of_birth else "",
        "color": patient.color,
        "microchip_id": patient.microchip_id or "",
        "allergies": patient.allergies,
        "owner_name": patient.owner.full_name,
        "owner_phone": patient.owner.phone,
        "owner_address": patient.owner.address,
        "owner_email": patient.owner.email,
    })


# ── Client portal ─────────────────────────────────────────────────────────────

@login_required
def my_patients(request):
    patients = Patient.objects.none()
    try:
        owner = Owner.objects.get(email=request.user.email)
        patients = owner.patients.select_related("species", "breed")
    except Owner.DoesNotExist:
        pass
    return render(request, "patients/my_patients.html", {"patients": patients})
