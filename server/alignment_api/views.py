from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from .models import Alignment, Link, SourceToken, TargetToken, Resource

from .serializers import (
    AlignmentSerializer,
    LinkSerializer,
    LinkReadSerializer,
    TargetTokenSerializer,
)
from rest_framework import viewsets, permissions, generics, status


class AlignmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows alignments to be viewed.
    """

    queryset = Alignment.objects.all()
    serializer_class = AlignmentSerializer


class TargetTokenViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = TargetTokenSerializer

    def get_queryset(self):
        resource_id = self.kwargs["resource"]
        resource = Resource.objects.get(id=resource_id)
        scopes = self.request.query_params.getlist("target_tokens")

        target_tokens_in_scope = []
        for scope in scopes:
            scoped_tokens = []
            scoped_tokens.extend(
                TargetToken.objects.filter(
                    token_id__startswith=scope, resource=resource
                )
            )
            target_tokens_in_scope.extend(scoped_tokens)

        return target_tokens_in_scope


class LinkList(generics.ListAPIView):
    """
    API endpoint that allows links to be viewed by alignment and scope.
    Scope is required.
    """

    def get_serializer_class(self):
        if self.request.method in ["GET"]:
            return LinkReadSerializer
        return LinkSerializer

    def get_queryset(self):
        alignment_id = self.kwargs["alignment"]
        alignment = Alignment.objects.get(id=alignment_id)
        scopes = self.request.query_params.getlist("source_token")

        source_tokens_in_scope = []
        for scope in scopes:
            scoped_tokens = SourceToken.objects.filter(
                token_id__startswith=scope, resource=alignment.source
            )
            source_tokens_in_scope.extend(scoped_tokens)

        return Link.objects.filter(
            alignment=alignment, source_tokens__in=source_tokens_in_scope
        )
