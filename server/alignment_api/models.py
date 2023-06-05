"""Define models for ER++.

To truncate/delete a table like Resource, use
>>> Resource.objects.all().delete()
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class Resource(models.Model):
    """Define Resource model.

    Resource here means a Bible, either in source language or a
    translation.

    """

    name = models.CharField(max_length=100)
    # restrict this to a 3-char ISO-639-3 code?
    lang = models.CharField(max_length=50)

    def __str__(self):
        """Return a string representation for self."""
        return "{self.id}: {self.name} ({self.lang})"


# class Token(models.Model):
#     token_id = models.CharField(max_length=15)
#     resource = models.ForeignKey("Resource", on_delete=models.SET_NULL,
#     null=True)
#     text = models.CharField(max_length=150)


class Subject(models.Model):
    """Define the Subject model.

    A subject describes the content of an image.
    """

    subject_id = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=256)
    description = models.CharField(max_length=256)


class SourceToken(models.Model):
    """Define the SourceToken model."""

    token_id = models.CharField(max_length=15)
    resource = models.ForeignKey("Resource", on_delete=models.SET_NULL, null=True)
    text = models.CharField(max_length=150, null=True)
    gloss = models.CharField(max_length=150, null=True)
    lemma = models.CharField(max_length=150, null=True)
    subjects = models.ManyToManyField(Subject, related_name="tokens")


class TargetToken(models.Model):
    """Define the TargetToken model."""

    token_id = models.CharField(max_length=15)
    resource = models.ForeignKey("Resource", on_delete=models.SET_NULL, null=True)
    text = models.CharField(max_length=150)
    is_punc = models.BooleanField(null=True)


class Alignment(models.Model):
    """Define the Alignment model."""

    name = models.CharField(max_length=256)
    source = models.ForeignKey(
        "Resource", related_name="source", on_delete=models.SET_NULL, null=True
    )
    target = models.ForeignKey(
        "Resource", related_name="target", on_delete=models.SET_NULL, null=True
    )
    type = models.CharField(max_length=150, null=True)


class Link(models.Model):
    """Define the Link model."""

    alignment = models.ForeignKey("Alignment", on_delete=models.SET_NULL, null=True)
    source_tokens = models.ManyToManyField(SourceToken, related_name="links")
    target_tokens = models.ManyToManyField(TargetToken, related_name="links")

    def __str__(self):
        """Return a string representation for self."""
        return "{self.alignment} {self.source_tokens} {self.target_tokens}"


class License(models.Model):
    """Define a license model.

    Best practice is a standard statement, but non-standard statements
    are also supported.

    """

    license_id = models.CharField(
        help_text="Unique identifier for a license statement.",
        max_length=256,
        unique=True,
    )
    license_url = models.URLField(
        help_text="The URL for a full license statement supporting an identifier.",
        blank=True,
    )
    attribution = models.BooleanField(
        help_text="Does this license require attribution?",
    )
    sharealike = models.BooleanField(
        help_text=(
            "Does this license require distributing your contributions under"
            " the same license as the original?"
        ),
    )
    noderivs = models.BooleanField(
        help_text="Does this license restrict you from distributing modified material?",
    )
    noncommercial = models.BooleanField(
        help_text=(
            "Does this license restrict you from using this material for commercial purposes?"
        ),
    )


class MediaAsset(models.Model):
    """Define the MediaAsset model."""

    # https://docs.djangoproject.com/en/4.2/ref/models/fields/#field-choices-enum-types
    class AssetType(models.TextChoices):
        """Define valid types for MediaAsset instances."""

        ART = "ART", _("Art")
        ARTICLE = "ARTICLE", _("Article")
        CHART = "CHART", _("Chart")
        MAP = "MAP", _("Map")
        PHOTO = "PHOTO", _("Photo")
        OTHER = "OTHER", _("Other")

    media_asset_id = models.SlugField(
        help_text=(
            "Unique identifier for this asset. Best practice is to use the"
            " publisher's value, if available."
        ),
        max_length=256,
        unique=True,
    )
    dam_id = models.SlugField(
        help_text="Identifier from backend storage for this asset.",
        max_length=128,
        unique=True,
    )

    # Publication attributes: these typically come from the publisher
    title = models.CharField(
        help_text="Publisher's English title for this asset.",
        max_length=256,
        blank=True,
    )
    subtitle = models.CharField(
        help_text="Publisher's English subtitle for this asset.",
        max_length=256,
        blank=True,
    )
    description = models.TextField(
        help_text="Publisher's English description for this asset.",
        blank=True,
    )
    publisher = models.CharField(
        help_text=(
            "The entity responsible for making this resource available."
            " Examples include a person, an organization, or a service."
            " Typically, the name of a Publisher should be used to indicate the"
            " entity."
        ),
        max_length=256,
        blank=True,
    )
    creator = models.CharField(
        help_text=(
            "The entity responsible for making this resource. Examples include"
            " a person, an organization, or a service. Typically, the name of a"
            " Creator should be used to indicate the entity."
        ),
        max_length=256,
        blank=True,
    )
    # is this right? Not sure if we should allow null licenses.
    license = models.ForeignKey(
        "License",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    copyright = models.CharField(
        help_text=(
            "The copyright statement provided by the publisher. Leave blank for"
            " public domain licenses."
        ),
        max_length=256,
        blank=True,
    )

    # Editorial attributes: handled by ER++
    asset_type = models.SlugField(
        help_text="The type of media.",
        max_length=12,
        choices=AssetType.choices,
    )
    subject = models.ManyToManyField(
        Subject,
        help_text="The primary subject that is illustrated by this item.",
    )

    def get_asset_type(self) -> AssetType:
        """Return the asset type for self."""
        # Get value from choices enum
        return self.AssetType[self.asset_type]
