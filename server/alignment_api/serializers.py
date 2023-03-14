from rest_framework import serializers
from .models import Alignment, Link, SourceToken, TargetToken


# Learn more: https://www.django-rest-framework.org/api-guide/relations/
class AlignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alignment
        fields = ["id", "name", "source", "target"]


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = ["alignment", "source_tokens", "target_tokens"]


class SourceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourceToken
        fields = ["id", "token_id", "resource", "text"]


class TargetTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = TargetToken
        fields = ["id", "token_id", "resource", "text"]


class LinkReadSerializer(LinkSerializer):
    source_tokens = SourceTokenSerializer(read_only=True, many=True)
    target_tokens = TargetTokenSerializer(read_only=True, many=True)
