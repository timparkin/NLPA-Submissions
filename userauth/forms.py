

from django import forms
from django.utils.translation import gettext_lazy as _
from .models import CustomUser
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column
from wagtail.users.forms import UserCreationForm, UserEditForm
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import locale
import logging

logger = logging.getLogger('django')

# Source: https://en.wikipedia.org/wiki/February_29
PRE = [
    'US',
    'TW',
]
POST = [
    'GB',
    'HK',
]


def get_country():
    code, _ = locale.getlocale()
    try:
        return code.split('_')[1]
    except IndexError:
        raise Exception('Country cannot be ascertained from locale.')


def get_leap_birthday(year):
    country = get_country()
    if country in PRE:
        return date(year, 2, 28)
    elif country in POST:
        return date(year, 3, 1)
    else:
        raise Exception('It is unknown whether your country treats leap year '
                      + 'birthdays as being on the 28th of February or '
                      + 'the 1st of March. Please consult your country\'s '
                      + 'legal code for in order to ascertain an answer.')
def age(dob, when):
    today = when
    years = today.year - dob.year

    try:
        birthday = date(today.year, dob.month, dob.day)
    except ValueError as e:
        if dob.month == 2 and dob.day == 29:
            birthday = get_leap_birthday(today.year)
        else:
            raise e

    if today < birthday:
        years -= 1
    return years

class WagtailUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        widgets = {'date_of_birth': forms.DateInput(attrs={'type':'date'})}


class WagtailUserEditForm(UserEditForm):
    class Meta(UserEditForm.Meta):
        model = CustomUser
        widgets = {'date_of_birth': forms.DateInput(attrs={'type':'date'})}

class SignupForm(forms.Form):

    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email=forms.EmailField(required=True)
    password1 = forms.CharField(widget=forms.PasswordInput)
    date_of_birth = forms.DateField(required=False,label="Date of Birth (if youth entrant)", widget=forms.TextInput(attrs={'class':'datetimepicsker','placeholder':'dd/mm/yyyy', 'type':'date', 'data-options':'{"disableMobile":true, "format":"dd/mm/yyyy"}'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

    class Meta:
        model=CustomUser
        fields=('username','first_name','last_name','email','date_of_birth','password1')

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.date_of_birth = self.cleaned_data['date_of_birth']
        print('user dob %s'% user.date_of_birth)
        print('user age %s'% relativedelta(date(2020, 12, 31), user.date_of_birth).years)
        user.is_young_entrant = False
        if user.date_of_birth is not None:
            user.is_young_entrant = relativedelta(date(2020, 12, 31), user.date_of_birth).years  < 17

        if user.is_young_entrant is True:
            print('user under 18')
        else:
            print('user is an oldie')
        user.save()

class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        #fields = ['first_name', 'last_name', 'display_name', 'date_of_birth', 'address1', 'address2', 'zip_code', 'city', 'country', 'mobile_phone', 'additional_information', 'photo',]
        #widgets = {'date_of_birth': forms.DateInput(attrs={'type':'date'})}
        fields = ['first_name', 'last_name', 'email']
