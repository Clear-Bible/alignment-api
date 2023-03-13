from rest_framework import serializers
from .models import Alignment, Link, SourceToken, TargetToken


# Learn more: https://www.django-rest-framework.org/api-guide/relations/
class AlignmentSerializer(serializers.ModelSerializer):
    source = serializers.StringRelatedField(many=False)
    target = serializers.StringRelatedField(many=False)

    class Meta:
        model = Alignment
        fields = ["name", "source", "target"]
