from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def index(request):
    return render(request, "reports/index.html")


@login_required
def vaccination_certificate(request, patient_pk):
    return render(request, "reports/coming_soon.html", {"title": "Certificado de vacunación"})


@login_required
def patient_history(request, patient_pk):
    return render(request, "reports/coming_soon.html", {"title": "Historia clínica"})


@login_required
def prescription_pdf(request, pk):
    return render(request, "reports/coming_soon.html", {"title": "Receta"})
