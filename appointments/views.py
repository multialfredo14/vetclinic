import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from accounts.mixins import RoleRequiredMixin
from .forms import AppointmentForm, AppointmentStatusForm, AppointmentTypeForm
from .models import Appointment, AppointmentType


# ── Appointment Types (admin) ─────────────────────────────────────────────────

class AppointmentTypeListView(RoleRequiredMixin, ListView):
    allowed_roles = ["Admin"]
    model = AppointmentType
    template_name = "appointments/type_list.html"
    context_object_name = "types"


class AppointmentTypeCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = ["Admin"]
    model = AppointmentType
    form_class = AppointmentTypeForm
    template_name = "appointments/type_form.html"
    success_url = reverse_lazy("appointments:type_list")

    def form_valid(self, form):
        messages.success(self.request, "Tipo de cita creado.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs, title="Nuevo tipo de cita")


class AppointmentTypeUpdateView(RoleRequiredMixin, UpdateView):
    allowed_roles = ["Admin"]
    model = AppointmentType
    form_class = AppointmentTypeForm
    template_name = "appointments/type_form.html"
    success_url = reverse_lazy("appointments:type_list")

    def form_valid(self, form):
        messages.success(self.request, "Tipo de cita actualizado.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs, title=f"Editar: {self.object.label}")


# ── Appointments ──────────────────────────────────────────────────────────────

class AppointmentListView(LoginRequiredMixin, ListView):
    model = Appointment
    template_name = "appointments/appointment_list.html"
    context_object_name = "appointments"
    paginate_by = 25

    def get_queryset(self):
        qs = Appointment.objects.select_related(
            "patient", "vet", "appointment_type"
        )
        status = self.request.GET.get("status", "")
        vet_id = self.request.GET.get("vet", "")
        date = self.request.GET.get("date", "")
        q = self.request.GET.get("q", "").strip()

        if not self.request.user.is_admin_user and not self.request.user.is_vet:
            pass  # Receptionist / assistant see all

        if status:
            qs = qs.filter(status=status)
        if vet_id:
            qs = qs.filter(vet_id=vet_id)
        if date:
            qs = qs.filter(scheduled_at__date=date)
        if q:
            qs = qs.filter(
                Q(patient__name__icontains=q) | Q(reason__icontains=q)
            )
        return qs.order_by("-scheduled_at")

    def get_context_data(self, **kwargs):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        ctx = super().get_context_data(**kwargs)
        ctx["status_choices"] = Appointment.STATUS_CHOICES
        ctx["vets"] = User.objects.filter(is_active=True).order_by("first_name")
        ctx["status_filter"] = self.request.GET.get("status", "")
        ctx["vet_filter"] = self.request.GET.get("vet", "")
        ctx["date_filter"] = self.request.GET.get("date", "")
        ctx["query"] = self.request.GET.get("q", "")
        return ctx


class AppointmentDetailView(LoginRequiredMixin, DetailView):
    model = Appointment
    template_name = "appointments/appointment_detail.html"
    context_object_name = "appointment"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["status_form"] = AppointmentStatusForm(instance=self.object)
        return ctx


class AppointmentCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = ["Admin", "Recepcionista", "Asistente Veterinario"]
    required_permission = "appointments.add_appointment"
    model = Appointment
    form_class = AppointmentForm
    template_name = "appointments/appointment_form.html"

    def get_initial(self):
        initial = super().get_initial()
        patient_pk = self.request.GET.get("patient")
        if patient_pk:
            initial["patient"] = patient_pk
        return initial

    def get_success_url(self):
        messages.success(self.request, "Cita creada correctamente.")
        return reverse_lazy("appointments:appointment_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs, title="Nueva cita")


class AppointmentUpdateView(RoleRequiredMixin, UpdateView):
    allowed_roles = ["Admin", "Recepcionista"]
    required_permission = "appointments.change_appointment"
    model = Appointment
    form_class = AppointmentForm
    template_name = "appointments/appointment_form.html"

    def get_success_url(self):
        messages.success(self.request, "Cita actualizada.")
        return reverse_lazy("appointments:appointment_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs, title=f"Editar cita #{self.object.pk}")


@login_required
def appointment_cancel(request, pk):
    user = request.user
    if not (user.is_admin_user or user.is_receptionist or user.has_perm("appointments.change_appointment")):
        messages.error(request, "No tienes permiso para cancelar citas.")
        return redirect("appointments:appointment_detail", pk=pk)
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == "POST":
        appointment.status = "cancelled"
        appointment.save()
        messages.success(request, "Cita cancelada.")
        return redirect("appointments:appointment_list")
    return render(request, "appointments/appointment_cancel.html", {"appointment": appointment})


@login_required
def appointment_update_status(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == "POST":
        form = AppointmentStatusForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, "Estado actualizado.")
    return redirect("appointments:appointment_detail", pk=pk)


# ── Calendar ──────────────────────────────────────────────────────────────────

@login_required
def calendar_view(request):
    return render(request, "appointments/calendar.html")


@login_required
def calendar_events(request):
    qs = Appointment.objects.select_related("patient", "appointment_type")
    events = []
    for appt in qs:
        from datetime import timedelta
        end = appt.scheduled_at + timedelta(minutes=appt.duration)
        events.append({
            "id": appt.pk,
            "title": str(appt.patient),
            "start": appt.scheduled_at.isoformat(),
            "end": end.isoformat(),
            "color": appt.appointment_type.color,
            "url": f"/appointments/{appt.pk}/",
            "extendedProps": {
                "type": appt.appointment_type.label,
                "status": appt.get_status_display(),
            },
        })
    return JsonResponse(events, safe=False)


# ── Client portal ─────────────────────────────────────────────────────────────

@login_required
def my_appointments(request):
    import datetime
    appointments = Appointment.objects.filter(
        patient__owner__email=request.user.email,
    ).select_related("patient", "appointment_type", "vet").order_by("scheduled_at")
    return render(request, "appointments/my_appointments.html", {
        "appointments": appointments,
        "today": datetime.date.today(),
    })
