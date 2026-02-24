from django.urls import path
from . import views

app_name = "parent"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("enfant/<int:etudiant_id>/edt/", views.edt_enfant, name="edt_enfant"),
    path("enfant/<int:etudiant_id>/notes/", views.notes_enfant, name="notes_enfant"),
    path("enfant/<int:etudiant_id>/assiduite/", views.assiduite_enfant, name="assiduite_enfant"),
    path("notifications/", views.notifications, name="notifications"),
]
