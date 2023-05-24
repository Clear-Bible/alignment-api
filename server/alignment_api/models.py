from django.db import models, connection
from django.utils.translation import gettext_lazy as _

# Create your models here.
class Resource(models.Model):
    name = models.CharField(max_length=100)
    lang = models.CharField(max_length=50)

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE {} CASCADE".format(cls._meta.db_table))

    def __str__(self):
        return "{}: {} ({})".format(self.id, self.name, self.lang)


# class Token(models.Model):
#     token_id = models.CharField(max_length=15)
#     resource = models.ForeignKey("Resource", on_delete=models.SET_NULL, null=True)
#     text = models.CharField(max_length=150)


class Subject(models.Model):
    subject_id = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=256)
    description = models.CharField(max_length=256)

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE {} CASCADE".format(cls._meta.db_table))


class SourceToken(models.Model):
    token_id = models.CharField(max_length=15)
    resource = models.ForeignKey("Resource", on_delete=models.SET_NULL, null=True)
    text = models.CharField(max_length=150, null=True)
    gloss = models.CharField(max_length=150, null=True)
    lemma = models.CharField(max_length=150, null=True)
    subjects = models.ManyToManyField(Subject, related_name="tokens")

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE {} CASCADE".format(cls._meta.db_table))


class TargetToken(models.Model):
    token_id = models.CharField(max_length=15)
    resource = models.ForeignKey("Resource", on_delete=models.SET_NULL, null=True)
    text = models.CharField(max_length=150)
    is_punc = models.BooleanField(null=True)

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE {} CASCADE".format(cls._meta.db_table))


class Alignment(models.Model):
    name = models.CharField(max_length=256)
    source = models.ForeignKey(
        "Resource", related_name="source", on_delete=models.SET_NULL, null=True
    )
    target = models.ForeignKey(
        "Resource", related_name="target", on_delete=models.SET_NULL, null=True
    )
    type = models.CharField(max_length=150, null=True)

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE {} CASCADE".format(cls._meta.db_table))


class Link(models.Model):
    alignment = models.ForeignKey("Alignment", on_delete=models.SET_NULL, null=True)
    source_tokens = models.ManyToManyField(SourceToken, related_name="links")
    target_tokens = models.ManyToManyField(TargetToken, related_name="links")

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE {} CASCADE".format(cls._meta.db_table))

    def __str__(self):
        return "{} {} {}".format(self.alignment, self.source_tokens, self.target_tokens)


class MediaAsset(models.Model):
    media_asset_id = models.CharField(max_length=256)
    dam_id = models.CharField(max_length=128)

    title = models.CharField(max_length=256)
    subtitle = models.CharField(max_length=256)
    description = models.CharField(max_length=256)

    class AssetType(models.TextChoices):
        PHOTO = "PHOTO", _("Photo")
        MAP = "MAP", _("Map")
        ART = "ART", _("Art")
        ARTICLE = "ARTICLE", _("Article")
        CHART = "CHART", _("Chart")

    asset_type = models.CharField(
        max_length=12,
        choices=AssetType.choices,
    )

    subject = models.ForeignKey(
        Subject,
        to_field="subject_id",
        db_column="subject",
        on_delete=models.SET_NULL,
        null=True,
    )

    # cf. https://stackoverflow.com/questions/54802616/how-can-one-use-enums-as-a-choice-field-in-a-django-model
    def get_asset_type(self) -> AssetType:
        # Get value from choices enum
        return self.AssetType[self.asset_type]

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE {} CASCADE".format(cls._meta.db_table))
