from django.db import models

# Create your models here.
class Resource(models.Model):
    name = models.CharField(max_length=100)
    lang = models.CharField(max_length=50)


# class Token(models.Model):
#     token_id = models.CharField(max_length=15)
#     resource = models.ForeignKey("Resource", on_delete=models.SET_NULL, null=True)
#     text = models.CharField(max_length=150)


class SourceToken(models.Model):
    token_id = models.CharField(max_length=15)
    resource = models.ForeignKey("Resource", on_delete=models.SET_NULL, null=True)
    text = models.CharField(max_length=150)


class TargetToken(models.Model):
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
    source_tokens = models.ManyToManyField(SourceToken, related_name="links")
    target_tokens = models.ManyToManyField(TargetToken, related_name="links")

    def __str__(self):
        return "{} {} {}".format(self.alignment, self.source_tokens, self.target_tokens)
