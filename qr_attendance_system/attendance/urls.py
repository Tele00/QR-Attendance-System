from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("create/", views.create, name="create"),
    path("delete/<int:id>", views.delete, name="delete"),
    path("downloadqr/<int:id>", views.download_qr, name="downloadqr"),
    path("downloadsheet/<int:id>", views.download_attendance, name="downloadattendance"),
    path("add/<int:id>", views.addstudent, name="addstudent"),
    path("scan/<int:id>", views.log_attendance, name="scan")
]