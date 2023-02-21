from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.


def get_alignments(request):
    print("get_existing_alignments")
    return HttpResponse("You've hit the existing alignments endpoint.")
