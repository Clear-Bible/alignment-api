from rest_framework import serializers
from .models import Alignment, Link, SourceToken, TargetToken


# Learn more: https://www.django-rest-framework.org/api-guide/relations/
class AlignmentSerializer(serializers.ModelSerializer):
    source = serializers.StringRelatedField(many=False)
    target = serializers.StringRelatedField(many=False)

    class Meta:
        model = Alignment
        fields = ["id", "name", "source", "target"]


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = ["alignment", "source_tokens", "target_tokens"]
