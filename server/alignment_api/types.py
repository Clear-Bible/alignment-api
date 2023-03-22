# types.py
import strawberry
from strawberry import auto
from typing import List
from . import models


@strawberry.django.type(models.Resource)
class Resource:
    id: auto
    name: auto
    lang: auto


@strawberry.django.type(models.SourceToken)
class SourceToken:
    token_id: auto
    resource: Resource
    text: auto
    gloss: auto
    lemma: auto


@strawberry.django.type(models.TargetToken)
class TargetToken:
    token_id: auto
    resource: Resource
    text: auto
    is_punc: auto


@strawberry.django.type(models.Alignment)
class Alignment:
    name: auto
    source: Resource
    target: Resource
    type: auto


@strawberry.django.type(models.Link)
class Link:
    alignment: Alignment
    source_tokens: List[SourceToken]
    target_tokens: List[TargetToken]
