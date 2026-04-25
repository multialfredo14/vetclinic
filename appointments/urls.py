from django.urls import path
from . import views

app_name = "appointments"

urlpatterns = [
    # Appointment types
    path("appointment-types/", views.AppointmentTypeListView.as_view(), name="type_list"),
    path("appointment-types/new/", views.AppointmentTypeCreateView.as_view(), name="type_create"),
    path("appointment-types/<int:pk>/edit/", views.AppointmentTypeUpdateView.as_view(), name="type_edit"),

    # Appointments
    path("appointments/", views.AppointmentListView.as_view(), name="appointment_list"),
    path("appointments/new/", views.AppointmentCreateView.as_view(), name="appointment_create"),
    path("appointments/<int:pk>/", views.AppointmentDetailView.as_view(), name="appointment_detail"),
    path("appointments/<int:pk>/edit/", views.AppointmentUpdateView.as_view(), name="appointment_edit"),
    path("appointments/<int:pk>/cancel/", views.appointment_cancel, name="appointment_cancel"),
    path("appointments/<int:pk>/status/", views.appointment_update_status, name="appointment_status"),

    # Calendar
    path("calendar/", views.calendar_view, name="calendar"),
    path("calendar/events/", views.calendar_events, name="calendar_events"),

    # Client portal
    path("my-appointments/", views.my_appointments, name="my_appointments"),
]
