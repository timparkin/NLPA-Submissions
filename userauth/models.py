from django.contrib.auth.models import AbstractUser, AbstractBaseUser
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from wagtail.admin.panels import FieldPanel


class CustomUser(AbstractUser):

    display_name = models.CharField(verbose_name=_("Your name"), max_length=1024, help_text=_("How you want your name to appear in social media or press releases"),default='')
    date_of_birth = models.DateField(verbose_name=_("Date of birth"), blank=True, null=True)
    address1 = models.CharField(verbose_name=_("Address line 1"), max_length=1024, blank=True, null=True)
    address2 = models.CharField(verbose_name=_("Address line 2"), max_length=1024, blank=True, null=True)
    city = models.CharField(verbose_name=_("City"), max_length=1024, blank=True, null=True)
    region = models.CharField(verbose_name=_("State/Region/County"), max_length=1024, blank=True, null=True)
    zip_code = models.CharField(verbose_name=_("Postal Code"), max_length=12, blank=True, null=True)
    country = CountryField(blank=True, null=True)
    location = models.CharField(verbose_name=_("Residence"), max_length=1024, blank=True, null=True, help_text = "Where you live as it will appear on our social media and press releases (e.g. 'California, US' or 'Yorkshire, UK'")

    phone_regex = RegexValidator(regex=r"^\+(?:[0-9]●?){6,14}[0-9]$", message=_("Enter a valid international mobile phone number starting with +(country code)"))
    mobile_phone = models.CharField(validators=[phone_regex], verbose_name=_("Mobile phone"), max_length=17, blank=True, null=True)
    additional_information = models.CharField(verbose_name=_("Additional information"), max_length=4096, blank=True, null=True)
    bio = models.CharField(verbose_name=_("Short Bio"), max_length=4096, blank=True, null=True, help_text = "A short profile of yourself as it will appear on our social media and press releases. One or two sentences please. ")
    instagram = models.CharField(verbose_name=_("Instagram"), max_length=1024, blank=True, null=True, default='')
    twitter = models.CharField(verbose_name=_("Twitter"), max_length=1024, blank=True, null=True, default='')
    Facebook = models.CharField(verbose_name=_("Facebook"), max_length=1024, blank=True, null=True, default='')
    facebook = models.CharField(verbose_name=_("Facebook"), max_length=1024, blank=True, null=True, default='')
    social_media_type = models.CharField(verbose_name=_("Social Media Type"), max_length=1024, blank=True, null=True, default='')
    social_media_link = models.CharField(verbose_name=_("Social Media Link"), max_length=1024, blank=True, null=True, default='')
    marketing_prefs = models.CharField(verbose_name=_("Marketing Preferences"), max_length=4096, blank=True, null=True)
    photo = models.ImageField(verbose_name=_("Photo"), upload_to='photos/', default='photos/default-user-avatar.png')
    website = models.CharField(verbose_name=_("Main Website"), max_length=1024, blank=True, null=True, default='')
    payment_status = models.CharField(verbose_name=_("Payment Status"), max_length=1024, blank=True, null=True)
    payment_plan = models.CharField(verbose_name=_("Payment Plan"), max_length=1024, blank=True, null=True)
    payment_upgrade_status = models.CharField(verbose_name=_("Payment Upgrade Status"), max_length=1024, blank=True, null=True)
    payment_upgrade_plan = models.CharField(verbose_name=_("Payment Upgrade Plan"), max_length=1024, blank=True, null=True)
    coupon = models.CharField(verbose_name=_("Coupon"), max_length=1024, blank=True, null=True)
    is_young_entrant = models.CharField(verbose_name=_("Is Young Entrant"), max_length=1024, blank=True, null=False, default='False')
    project_title_one = models.CharField(verbose_name=_("Project Title One"), max_length=1024, blank=True, null=True)
    project_description_one = models.TextField(verbose_name=_("Project Description One"), blank=True, null=True)
    project_title_two = models.CharField(verbose_name=_("Project Title Two"), max_length=1024, blank=True, null=True)
    project_description_two = models.TextField(verbose_name=_("Project Description Two"), blank=True, null=True)

    panels = [
        FieldPanel('payment_status'),
        FieldPanel('payment_plan'),
    ]

    class Meta:
        ordering = ['last_name']

    def get_absolute_url(self):
        return reverse('account_profile')

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

class Year(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    year = models.IntegerField(verbose_name=_("Competition Year"), blank=True, null=True)
    payment_status = models.CharField(verbose_name=_("Payment Status"), max_length=1024, blank=True, null=True)
    payment_plan = models.CharField(verbose_name=_("Payment Plan"), max_length=1024, blank=True, null=True)
    payment_upgrade_status = models.CharField(verbose_name=_("Payment Upgrade Status"), max_length=1024, blank=True, null=True)
    payment_upgrade_plan = models.CharField(verbose_name=_("Payment Upgrade Plan"), max_length=1024, blank=True, null=True)
    is_young_entrant = models.CharField(verbose_name=_("Is Young Entrant"), max_length=1024, blank=True, null=False, default='False')
    project_title_one = models.CharField(verbose_name=_("Project Title One"), max_length=1024, blank=True, null=True)
    project_description_one = models.TextField(verbose_name=_("Project Description One"), blank=True, null=True)
    project_title_two = models.CharField(verbose_name=_("Project Title Two"), max_length=1024, blank=True, null=True)
    project_description_two = models.TextField(verbose_name=_("Project Description Two"), blank=True, null=True)

    def __str__(self):
        return str(self.year)

    class Meta:
        ordering = ['year']
