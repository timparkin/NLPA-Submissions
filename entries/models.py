from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions

from userauth.models import CustomUser

from thumbnails.fields import ImageField

from multiselectfield import MultiSelectField


class Entry(models.Model):

    class Categories(models.TextChoices):
        grand_scenic = 'GS', _('Grand Scenic')
        intimate_landscapes = 'IL', _('Intimate Landscapes')
        abstracts_and_details = 'AD', _('Abstracts & Details')

    class SpecialAward(models.TextChoices):
        wildlife = 'EW', _('Environmental Wildlife')
        creative = 'CI', _('Creative Icon')
        common_places = 'CP', _('Common Places')
        mountains = 'M', _('Mountains')
        water_worlds = 'W', _('Water Worlds')
        black_and_white = 'BW', _('Black and White')
        nightscape = 'N', _('Nightscape')
        environmental = 'E', _('Environmental')
        aerial = 'A', _('Aerial')



    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True)
    category = models.CharField(verbose_name=_("Category"), max_length=128, choices=Categories.choices, default=Categories.grand_scenic, blank=True, null=True)
    special_award = MultiSelectField(verbose_name=_("Special Award (<a href=\"https://naturallandscapeawards.com/categories#special_awards\" target=\"_blank\">more info</a>)"), max_length=256, choices=SpecialAward.choices, default='', blank=True, null=True)
    filename = models.CharField(verbose_name=_("Filename"), max_length=128, default='', blank=True, null=True)
    photo_size = models.CharField(verbose_name=_("Photo Size"), max_length=1024, default='', blank=True, null=True)
    photo_dimensions = models.CharField(verbose_name=_("Photo Dimensions"), max_length=1024, default='', blank=True, null=True)
    photo = models.ImageField(verbose_name=_("Photo"), upload_to='entries/', default='entries/default-entry.png', max_length=500)
    datetime = models.DateTimeField(verbose_name=_("Uploaded date"), auto_now_add=True, null=True)
    description = models.CharField(verbose_name=_("Description"), max_length=2048, blank=True, null=True)
    title = models.CharField(verbose_name=_("Title"), max_length=128, default='Untitled')
    year = models.IntegerField(verbose_name=_("Competition Year"), blank=True, null=True)
    project_id = models.CharField(verbose_name=_("Project Identifier"), max_length=128) # this will be 1 or 2
    internal_notes = models.CharField(verbose_name=_("Notes"), max_length=2048, blank=True, null=True)

    # Extra fields for the final rounds
    in_second_round = models.BooleanField(verbose_name=_("In Second Round"), null=False, default=False)
    passed_checks = models.BooleanField(verbose_name=_("Passed Checks"), max_length=1024, blank=True, null=False, default=False)
    evidence_file_1 = models.FileField(verbose_name=_("Verification #1"), upload_to='raws/', default='raws/default-entry.png', blank=True, null=True)
    evidence_file_2 = models.FileField(verbose_name=_("Verification #2"), upload_to='raws/', default='raws/default-entry.png', blank=True, null=True)
    evidence_file_3 = models.FileField(verbose_name=_("Verification #3"), upload_to='raws/', default='raws/default-entry.png', blank=True, null=True)
    evidence_file_4 = models.FileField(verbose_name=_("Verification #4"), upload_to='raws/', default='raws/default-entry.png', blank=True, null=True)
    evidence_file_5 = models.FileField(verbose_name=_("Verification #5"), upload_to='raws/', default='raws/default-entry.png', blank=True, null=True)
    ef1_filename = models.CharField(verbose_name=_("IV1 Filename"), max_length=128, default='', blank=True, null=True)
    ef2_filename = models.CharField(verbose_name=_("IV2 Filename"), max_length=128, default='', blank=True, null=True)
    ef3_filename = models.CharField(verbose_name=_("IV3 Filename"), max_length=128, default='', blank=True, null=True)
    ef4_filename = models.CharField(verbose_name=_("IV4 Filename"), max_length=128, default='', blank=True, null=True)
    ef5_filename = models.CharField(verbose_name=_("IV5 Filename"), max_length=128, default='', blank=True, null=True)
    in_book = models.BooleanField(verbose_name=_("In Book"), max_length=1024, blank=True, null=False, default=False)


    class Meta:
        ordering = ['datetime']
