from django.urls import path
from . import views

app_name = "patients"

urlpatterns = [
    # Owners
    path("owners/", views.OwnerListView.as_view(), name="owner_list"),
    path("owners/new/", views.OwnerCreateView.as_view(), name="owner_create"),
    path("owners/<int:pk>/", views.OwnerDetailView.as_view(), name="owner_detail"),
    path("owners/<int:pk>/edit/", views.OwnerUpdateView.as_view(), name="owner_edit"),
    path("owners/<int:pk>/delete/", views.OwnerDeleteView.as_view(), name="owner_delete"),

    # Patients
    path("patients/", views.PatientListView.as_view(), name="patient_list"),
    path("patients/new/", views.PatientCreateView.as_view(), name="patient_create"),
    path("patients/<int:pk>/", views.PatientDetailView.as_view(), name="patient_detail"),
    path("patients/<int:pk>/edit/", views.PatientUpdateView.as_view(), name="patient_edit"),
    path("patients/<int:pk>/delete/", views.PatientDeleteView.as_view(), name="patient_delete"),

    # AJAX
    path("api/breeds/", views.breeds_by_species, name="breeds_by_species"),
    path("api/patients/<int:pk>/", views.patient_json, name="patient_json"),

    # Client portal
    path("my-patients/", views.my_patients, name="my_patients"),
]
