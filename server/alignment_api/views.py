from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from .models import Alignment, Link

# Create your views here.


def convert_tokens(tokens):
    returned_tokens = []
    for token in tokens:
        returned_tokens.append(
            {
                "tokenId": token["token_id"],
                "resourceId": token["resource_id"],
                "text": token["text"],
            }
        )
    return returned_tokens


def convert_links(links):
    converted_links = []
    for link in links:
        converted_link = {}
        converted_link["id"] = link.id
        converted_link["sourceTokens"] = convert_tokens(link.source_tokens.values())
        converted_link["targetTokens"] = convert_tokens(link.target_tokens.values())
        converted_links.append(converted_link)
    return converted_links


def get_alignments(request):
    print("get_existing_alignments")
    alignments = Alignment.objects.all()
    response = {}
    response["alignments"] = []

    for alignment in alignments:
        simplified_alignment = {}
        links = []

        simplified_alignment["id"] = alignment.name
        simplified_alignment["source"] = alignment.source.name
        simplified_alignment["target"] = alignment.target.name
        simplified_alignment["linkNum"] = alignment.link_set.all().count()

        # simplified_alignment["links"] = convert_links(alignment.link_set.all())
        response["alignments"].append(simplified_alignment)

    return JsonResponse(response)
