"""Define admin interface."""

from django.contrib import admin

from .models import Subject, License, MediaAsset

admin.site.register(Subject)
admin.site.register(License)
admin.site.register(MediaAsset)
