from django.contrib.auth.models import AbstractUser, AbstractBaseUser
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField


class CustomUser(AbstractUser):

    display_name = models.CharField(verbose_name=_("Display name"), max_length=30, help_text=_("Will be shown e.g. when commenting"),default='Display Name')
    date_of_birth = models.DateField(verbose_name=_("Date of birth"), blank=True, null=True)
    address1 = models.CharField(verbose_name=_("Address line 1"), max_length=1024, blank=True, null=True)
    address2 = models.CharField(verbose_name=_("Address line 2"), max_length=1024, blank=True, null=True)
    city = models.CharField(verbose_name=_("City"), max_length=1024, blank=True, null=True)
    region = models.CharField(verbose_name=_("State/Region/County"), max_length=1024, blank=True, null=True)
    zip_code = models.CharField(verbose_name=_("Postal Code"), max_length=12, blank=True, null=True)
    country = CountryField(blank=True, null=True)
    phone_regex = RegexValidator(regex=r"^\+(?:[0-9]●?){6,14}[0-9]$", message=_("Enter a valid international mobile phone number starting with +(country code)"))
    mobile_phone = models.CharField(validators=[phone_regex], verbose_name=_("Mobile phone"), max_length=17, blank=True, null=True)
    additional_information = models.CharField(verbose_name=_("Additional information"), max_length=4096, blank=True, null=True)
    bio = models.CharField(verbose_name=_("Short Bio"), max_length=4096, blank=True, null=True)
    instagram = models.CharField(verbose_name=_("Instagram"), max_length=1024, blank=True, null=True)
    twitter = models.CharField(verbose_name=_("Twitter"), max_length=1024, blank=True, null=True)
    Facebook = models.CharField(verbose_name=_("Facebook"), max_length=1024, blank=True, null=True)
    marketing_prefs = models.CharField(verbose_name=_("Marketing Preferences"), max_length=4096, blank=True, null=True)
    photo = models.ImageField(verbose_name=_("Photo"), upload_to='photos/', default='photos/default-user-avatar.png')
    website = models.CharField(verbose_name=_("Main Website"), max_length=1024, blank=True, null=True)

    class Meta:
        ordering = ['last_name']

    def get_absolute_url(self):
        return reverse('account_profile')

    def __str__(self):
        return f"{self.username}: {self.first_name} {self.last_name}"
