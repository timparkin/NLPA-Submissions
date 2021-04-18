from django.db import models
from django.utils.translation import gettext_lazy as _

from userauth.models import CustomUser


class Entry(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    photo = models.ImageField(verbose_name=_("Entry Photo"), upload_to='entries/', default='photos/default-entry.jpg')
    datetime = models.DateTimeField(verbose_name=_("Uploaded date"), auto_now_add=True, null=True)
    description = models.CharField(verbose_name=_("Description"), max_length=2048, blank=True, null=True)
    title = models.CharField(verbose_name=_("Title"), max_length=128, default='Untitled')
    competition_year = models.IntegerField(verbose_name=_("Competition Year"), blank=True, null=True)
    competition_category = models.CharField(verbose_name=_("Competition Category"), blank=True, null=True)
    project_id = models.CharField(verbose_name=_("Project Identifier"), max_length=128)
    internal_notes = models.CharField(verbose_name=_("Notes"), max_length=2048, blank=True, null=True)

    class Meta:
        ordering = ['datetime']
