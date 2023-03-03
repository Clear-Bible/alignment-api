from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from .models import Alignment

# Create your views here.


def get_alignments(request):
    print("get_existing_alignments")
    alignments = Alignment.objects.all()
    response = {}
    response["alignments"] = []

    for alignment in alignments:
        simplified_alignment = {}
        simplified_alignment["id"] = alignment.name
        simplified_alignment["source"] = alignment.source.name
        simplified_alignment["target"] = alignment.target.name
        response["alignments"].append(simplified_alignment)

    return JsonResponse(response)
    # return HttpResponse("You've hit the existing alignments endpoint.")
