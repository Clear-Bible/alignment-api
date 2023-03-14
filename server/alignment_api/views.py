from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from .models import Alignment, Link, SourceToken, TargetToken

from .serializers import AlignmentSerializer, LinkSerializer
from rest_framework import viewsets, permissions, generics, status

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


class AlignmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows alignments to be viewed.
    """

    queryset = Alignment.objects.all()
    serializer_class = AlignmentSerializer
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]


def get_alignments(request):
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


def get_alignment(request, alignment_name):
    alignment = Alignment.objects.get(name=alignment_name)
    response = {}
    response["id"] = alignment.name
    response["source"] = alignment.source.name
    response["target"] = alignment.target.name
    response["linkNum"] = alignment.link_set.all().count()
    return JsonResponse(response)


class LinkList(generics.ListAPIView):
    """
    API endpoint that allows links to be viewed by alignment and scope.
    """

    serializer_class = LinkSerializer

    def get_queryset(self):
        print("MIKEY", self.kwargs)
        alignment_id = self.kwargs["alignment"]
        alignment = Alignment.objects.get(id=alignment_id)
        print(f"found alignment {alignment}")
        scopes = self.request.query_params.getlist("source_token")
        print("MIKEY", scopes)

        source_tokens_in_scope = []
        for scope in scopes:
            scoped_tokens = SourceToken.objects.filter(
                token_id__startswith=scope, resource=alignment.source
            )
            source_tokens_in_scope.extend(scoped_tokens)

        print(f" num scoped: {len(source_tokens_in_scope)}")
        return Link.objects.filter(
            alignment=alignment, source_tokens__in=source_tokens_in_scope
        )


def get_links(request, alignment_name):
    # Return specified links or a few random ones
    source_token_ids = request.GET.getlist("source_tokens", "")
    alignment = Alignment.objects.get(name=alignment_name)

    source_tokens = []
    for source_token_id in source_token_ids:
        found_tokens = SourceToken.objects.filter(
            token_id__startswith=source_token_id, resource=alignment.source
        )
        source_tokens.extend(found_tokens)

    links = []
    for source_token in source_tokens:
        links.extend(source_token.links.all())

    response = {}
    response["linkNum"] = len(links)
    response["links"] = convert_links(links)
    return JsonResponse(response)
