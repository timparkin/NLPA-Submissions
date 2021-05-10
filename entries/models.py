from django.db import models
from django.utils.translation import gettext_lazy as _

from userauth.models import CustomUser

from thumbnails.fields import ImageField


class Entry(models.Model):

    class Categories(models.TextChoices):
        grand_landscape = 'GL', _('Grand Landscape')
        intimate = 'IA', _('Intimate and Abstract')
        nightscape = 'N', _('Nightscape')
        aerial = 'A', _('Aerial')
#        portfolio_1 = 'P1', _('Portfolio One')
#        portfolio_2 = 'P2', _('Portfolio Two')


    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True)
    category = models.CharField(verbose_name=_("Category"), max_length=128, choices=Categories.choices, default=Categories.grand_landscape, blank=True, null=True)
    filename = models.CharField(verbose_name=_("Filename"), max_length=128, default='', blank=True, null=True)
    photo_size = models.CharField(verbose_name=_("Photo Size"), max_length=1024, default='', blank=True, null=True)
    photo_dimensions = models.CharField(verbose_name=_("Photo Dimensions"), max_length=1024, default='', blank=True, null=True)
    photo = models.ImageField(verbose_name=_("Entry Photo"), upload_to='entries/', default='entries/default-entry.png', max_length=500)
    datetime = models.DateTimeField(verbose_name=_("Uploaded date"), auto_now_add=True, null=True)
    description = models.CharField(verbose_name=_("Description"), max_length=2048, blank=True, null=True)
    title = models.CharField(verbose_name=_("Title"), max_length=128, default='Untitled')
    year = models.IntegerField(verbose_name=_("Competition Year"), blank=True, null=True)
    project_id = models.CharField(verbose_name=_("Project Identifier"), max_length=128) # this will be 1 or 2
    internal_notes = models.CharField(verbose_name=_("Notes"), max_length=2048, blank=True, null=True)

    class Meta:
        ordering = ['datetime']
