from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    LoginView as BaseLoginView,
    LogoutView as BaseLogoutView,
    PasswordResetView as BasePasswordResetView,
    PasswordResetDoneView as BasePasswordResetDoneView,
    PasswordResetConfirmView as BasePasswordResetConfirmView,
    PasswordResetCompleteView as BasePasswordResetCompleteView,
)
from django.shortcuts import render
from django.urls import reverse_lazy

from .forms import LoginForm, CustomPasswordResetForm, CustomSetPasswordForm


class LoginView(BaseLoginView):
    form_class = LoginForm
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


class LogoutView(BaseLogoutView):
    next_page = reverse_lazy("accounts:login")


class PasswordResetView(BasePasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = "accounts/password_reset.html"
    email_template_name = "accounts/email/password_reset_email.txt"
    subject_template_name = "accounts/email/password_reset_subject.txt"
    success_url = reverse_lazy("accounts:password_reset_done")


class PasswordResetDoneView(BasePasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"


class PasswordResetConfirmView(BasePasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = "accounts/password_reset_confirm.html"
    success_url = reverse_lazy("accounts:password_reset_complete")


class PasswordResetCompleteView(BasePasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"


@login_required
def dashboard(request):
    from appointments.models import Appointment
    from patients.models import Patient, Owner
    from inventory.models import Product
    import datetime

    user = request.user
    today = datetime.date.today()
    ctx = {"today": today}

    if user.is_admin_user or user.is_vet or user.is_assistant or user.is_receptionist:
        ctx["total_patients"] = Patient.objects.filter(deceased=False).count()
        ctx["total_owners"] = Owner.objects.count()
        ctx["today_appointments"] = (
            Appointment.objects.filter(scheduled_at__date=today)
            .select_related("patient", "vet", "appointment_type")
            .order_by("scheduled_at")
        )
        ctx["pending_appointments"] = Appointment.objects.filter(
            status__in=("scheduled", "confirmed")
        ).count()

    if user.is_admin_user:
        from django.db.models import F
        ctx["low_stock_list"] = Product.objects.filter(stock__lte=F("min_stock"))[:5]

    if user.is_client:
        try:
            owner = Owner.objects.get(email=user.email)
            ctx["my_patients"] = Patient.objects.filter(owner=owner, deceased=False)
            ctx["my_appointments"] = Appointment.objects.filter(
                patient__owner=owner,
                scheduled_at__date__gte=today,
            ).select_related("patient", "appointment_type").order_by("scheduled_at")[:5]
        except Owner.DoesNotExist:
            ctx["my_patients"] = Patient.objects.none()
            ctx["my_appointments"] = Appointment.objects.none()

    return render(request, "dashboard.html", ctx)
