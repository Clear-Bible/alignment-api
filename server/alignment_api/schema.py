# schema.py
import strawberry
from typing import List
from .types import Resource


@strawberry.type
class Query:
    resources: List[Resource] = strawberry.django.field()


schema = strawberry.Schema(query=Query)
