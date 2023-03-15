from django.db import models, connection

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


class SourceToken(models.Model):
    token_id = models.CharField(max_length=15)
    resource = models.ForeignKey("Resource", on_delete=models.SET_NULL, null=True)
    text = models.CharField(max_length=150, null=True)
    gloss = models.CharField(max_length=150, null=True)
    lemma = models.CharField(max_length=150, null=True)

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
