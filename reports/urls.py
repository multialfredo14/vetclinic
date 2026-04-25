from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("reports/", views.index, name="index"),
    path("reports/vaccination-certificate/<int:patient_pk>/", views.vaccination_certificate, name="vaccination_certificate"),
    path("reports/patient-history/<int:patient_pk>/", views.patient_history, name="patient_history"),
    path("reports/prescription/<int:pk>/pdf/", views.prescription_pdf, name="prescription_pdf"),
]
