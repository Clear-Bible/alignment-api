from django.urls import path

from . import views

urlpatterns = [
    path("", views.get_alignments, name="get_alignments"),
]
