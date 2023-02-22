from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

# Create your views here.


def get_alignments(request):
    print("get_existing_alignments")
    return JsonResponse({"alignments": ["alignment1", "alignment2"]})
    # return HttpResponse("You've hit the existing alignments endpoint.")
