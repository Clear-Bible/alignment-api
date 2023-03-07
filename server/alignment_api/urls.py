from django.urls import path

from . import views

urlpatterns = [
    path("", views.get_alignments, name="get_alignments"),
    path("<slug:alignment_name>/", views.get_alignment, name="get_alignment"),
]
