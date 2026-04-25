from django.urls import path
from . import views

app_name = "medical"

urlpatterns = [
    # Consultations
    path("consultations/", views.ConsultationListView.as_view(), name="consultation_list"),
    path("consultations/new/", views.ConsultationCreateView.as_view(), name="consultation_create"),
    path("consultations/<int:pk>/", views.ConsultationDetailView.as_view(), name="consultation_detail"),
    path("consultations/<int:pk>/edit/", views.ConsultationUpdateView.as_view(), name="consultation_edit"),

    # Vaccinations
    path("vaccinations/", views.VaccinationListView.as_view(), name="vaccination_list"),
    path("vaccinations/new/", views.VaccinationCreateView.as_view(), name="vaccination_create"),

    # Prescriptions
    path("prescriptions/", views.PrescriptionListView.as_view(), name="prescription_list"),
    path("prescriptions/new/", views.prescription_create, name="prescription_create"),
    path("prescriptions/<int:pk>/", views.PrescriptionDetailView.as_view(), name="prescription_detail"),

    # Lab results
    path("lab/", views.LabResultListView.as_view(), name="lab_list"),
    path("lab/new/", views.LabResultCreateView.as_view(), name="lab_create"),
]
