from django.db import models

# Create your models here.
class Resource(models.Model):
    name = models.CharField(max_length=100)
    lang = models.CharField(max_length=50)


class Token(models.Model):
    token_id = models.CharField(max_length=15)
    resource = models.ForeignKey("Resource", on_delete=models.SET_NULL, null=True)
    text = models.CharField(max_length=150)


class Alignment(models.Model):
    name = models.CharField(max_length=256)
    source = models.ForeignKey(
        "Resource", related_name="source", on_delete=models.SET_NULL, null=True
    )
    target = models.ForeignKey(
        "Resource", related_name="target", on_delete=models.SET_NULL, null=True
    )


class Link(models.Model):
    alignment = models.ForeignKey("Alignment", on_delete=models.SET_NULL, null=True)
    sourceTokens = models.ManyToManyField("Token", related_name="sourceTokens")
    targetTokens = models.ManyToManyField("Token", related_name="targetTokens")
