import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from accounts.mixins import RoleRequiredMixin
from inventory.models import Product, StockMovement
from .forms import (
    ConsultationForm, VaccinationRecordForm,
    PrescriptionForm, PrescriptionItemFormSet, LabResultForm,
)
from .models import Consultation, VaccinationRecord, Prescription, LabResult


# ── Helpers ───────────────────────────────────────────────────────────────────

def _deduct_stock(product_name, product_type, quantity, user, reference_id, reason):
    """Find a matching inventory product and deduct stock."""
    product = Product.objects.filter(
        name__icontains=product_name, product_type=product_type
    ).first()
    if product and product.stock >= quantity:
        StockMovement.objects.create(
            product=product,
            reason=reason,
            quantity=-quantity,
            performed_by=user,
            reference_id=reference_id,
        )


def _save_vitals(consultation):
    """Mirror consultation vitals to VitalsHistory."""
    from .models import VitalsHistory
    if any([consultation.weight, consultation.temperature, consultation.heart_rate]):
        VitalsHistory.objects.create(
            patient=consultation.patient,
            recorded_at=datetime.datetime.combine(consultation.date, datetime.time()),
            weight=consultation.weight,
            temperature=consultation.temperature,
            heart_rate=consultation.heart_rate,
        )


# ── Consultations ─────────────────────────────────────────────────────────────

class ConsultationListView(LoginRequiredMixin, ListView):
    model = Consultation
    template_name = "medical/consultation_list.html"
    context_object_name = "consultations"
    paginate_by = 25

    def get_queryset(self):
        qs = Consultation.objects.select_related("patient", "vet")
        q = self.request.GET.get("q", "").strip()
        date = self.request.GET.get("date", "")
        if q:
            qs = qs.filter(
                Q(patient__name__icontains=q) | Q(diagnosis__icontains=q)
            )
        if date:
            qs = qs.filter(date=date)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["query"] = self.request.GET.get("q", "")
        ctx["date_filter"] = self.request.GET.get("date", "")
        return ctx


class ConsultationDetailView(LoginRequiredMixin, DetailView):
    model = Consultation
    template_name = "medical/consultation_detail.html"
    context_object_name = "consultation"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["prescriptions"] = self.object.prescriptions.prefetch_related("items__medication")
        ctx["today"] = datetime.date.today()
        return ctx


class ConsultationCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = ["Admin", "Veterinario", "Asistente Veterinario"]
    required_permission = "medical.add_consultation"
    model = Consultation
    form_class = ConsultationForm
    template_name = "medical/consultation_form.html"

    def get_initial(self):
        initial = super().get_initial()
        initial["patient"] = self.request.GET.get("patient")
        initial["appointment"] = self.request.GET.get("appointment")
        if self.request.user.is_vet:
            initial["vet"] = self.request.user
        return initial

    def form_valid(self, form):
        response = super().form_valid(form)
        _save_vitals(self.object)
        # Mark linked appointment in-progress if still scheduled/confirmed
        if self.object.appointment:
            appt = self.object.appointment
            if appt.status in ("scheduled", "confirmed"):
                appt.status = "in_progress"
                appt.save(update_fields=["status"])
        messages.success(self.request, f"Consulta registrada para {self.object.patient}.")
        return response

    def get_success_url(self):
        return reverse("medical:consultation_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Nueva consulta"
        return ctx


class ConsultationUpdateView(RoleRequiredMixin, UpdateView):
    allowed_roles = ["Admin", "Veterinario"]
    model = Consultation
    form_class = ConsultationForm
    template_name = "medical/consultation_form.html"

    def get_success_url(self):
        messages.success(self.request, "Consulta actualizada.")
        return reverse("medical:consultation_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = f"Editar consulta — {self.object.patient}"
        return ctx


# ── Vaccinations ──────────────────────────────────────────────────────────────

class VaccinationListView(LoginRequiredMixin, ListView):
    model = VaccinationRecord
    template_name = "medical/vaccination_list.html"
    context_object_name = "vaccinations"
    paginate_by = 30

    def get_queryset(self):
        qs = VaccinationRecord.objects.select_related("patient", "vaccine", "applied_by")
        q = self.request.GET.get("q", "").strip()
        overdue = self.request.GET.get("overdue", "")
        if q:
            qs = qs.filter(
                Q(patient__name__icontains=q) | Q(vaccine__name__icontains=q)
            )
        if overdue:
            qs = qs.filter(next_due_date__lt=datetime.date.today())
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["query"] = self.request.GET.get("q", "")
        ctx["overdue_filter"] = self.request.GET.get("overdue", "")
        ctx["today"] = datetime.date.today()
        return ctx


class VaccinationCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = ["Admin", "Veterinario", "Asistente Veterinario"]
    required_permission = "medical.add_vaccinationrecord"
    model = VaccinationRecord
    form_class = VaccinationRecordForm
    template_name = "medical/vaccination_form.html"

    def get_initial(self):
        initial = super().get_initial()
        initial["patient"] = self.request.GET.get("patient")
        initial["applied_by"] = self.request.user
        return initial

    def form_valid(self, form):
        response = super().form_valid(form)
        # Deduct vaccine from inventory
        _deduct_stock(
            self.object.vaccine.name, "vaccine", 1,
            self.request.user, self.object.pk, "vaccination",
        )
        messages.success(self.request, f"Vacunación registrada para {self.object.patient}.")
        return response

    def get_success_url(self):
        next_url = self.request.GET.get("next")
        if next_url:
            return next_url
        return reverse("patients:patient_detail", kwargs={"pk": self.object.patient.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Registrar vacunación"
        return ctx


# ── Prescriptions ─────────────────────────────────────────────────────────────

class PrescriptionListView(LoginRequiredMixin, ListView):
    model = Prescription
    template_name = "medical/prescription_list.html"
    context_object_name = "prescriptions"
    paginate_by = 25

    def get_queryset(self):
        qs = Prescription.objects.select_related(
            "consultation__patient", "issued_by"
        )
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(consultation__patient__name__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["query"] = self.request.GET.get("q", "")
        return ctx


class PrescriptionDetailView(LoginRequiredMixin, DetailView):
    model = Prescription
    template_name = "medical/prescription_detail.html"
    context_object_name = "prescription"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["items"] = self.object.items.select_related("medication")
        return ctx


@login_required
def prescription_create(request):
    u = request.user
    if not (u.is_admin_user or u.is_vet or u.has_perm("medical.add_prescription")):
        return HttpResponseForbidden()

    consultation_pk = request.GET.get("consultation")
    initial_consultation = None
    if consultation_pk:
        initial_consultation = get_object_or_404(Consultation, pk=consultation_pk)

    if request.method == "POST":
        form = PrescriptionForm(request.POST)
        formset = PrescriptionItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            prescription = form.save(commit=False)
            prescription.issued_by = request.user
            prescription.save()
            items = formset.save(commit=False)
            for item in items:
                item.prescription = prescription
                item.save()
                _deduct_stock(
                    item.medication.name, "medicine", 1,
                    request.user, prescription.pk, "prescription",
                )
            for obj in formset.deleted_objects:
                obj.delete()
            messages.success(request, "Receta creada.")
            return redirect("medical:prescription_detail", pk=prescription.pk)
    else:
        initial = {}
        if initial_consultation:
            initial["consultation"] = initial_consultation
        form = PrescriptionForm(initial=initial)
        formset = PrescriptionItemFormSet()

    return render(request, "medical/prescription_form.html", {
        "form": form,
        "formset": formset,
        "title": "Nueva receta",
        "consultation": initial_consultation,
    })


# ── Lab Results ───────────────────────────────────────────────────────────────

class LabResultListView(LoginRequiredMixin, ListView):
    model = LabResult
    template_name = "medical/lab_list.html"
    context_object_name = "results"
    paginate_by = 25

    def get_queryset(self):
        qs = LabResult.objects.select_related("patient", "ordered_by")
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(patient__name__icontains=q) | Q(test_name__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["query"] = self.request.GET.get("q", "")
        return ctx


class LabResultCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = ["Admin", "Veterinario"]
    required_permission = "medical.add_labresult"
    model = LabResult
    form_class = LabResultForm
    template_name = "medical/lab_form.html"

    def get_initial(self):
        initial = super().get_initial()
        initial["patient"] = self.request.GET.get("patient")
        initial["ordered_by"] = self.request.user
        return initial

    def form_valid(self, form):
        messages.success(self.request, "Resultado de laboratorio registrado.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("patients:patient_detail", kwargs={"pk": self.object.patient.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Nuevo resultado de laboratorio"
        return ctx
