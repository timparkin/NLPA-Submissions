

from django import forms
from django.utils.translation import gettext_lazy as _
from .models import CustomUser
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column
from wagtail.users.forms import UserCreationForm, UserEditForm


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
    date_of_birth = forms.DateField(required=False,label="Date of Birth (if youth entrant)", widget=forms.TextInput(attrs={'class':'datetimepicsker','placeholder':'d/m/y', 'type':'date', 'data-options':'{"disableMobile":true, "format":"mm/dd/yyyy"}'}))


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
        user.save()

class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        #fields = ['first_name', 'last_name', 'display_name', 'date_of_birth', 'address1', 'address2', 'zip_code', 'city', 'country', 'mobile_phone', 'additional_information', 'photo',]
        #widgets = {'date_of_birth': forms.DateInput(attrs={'type':'date'})}
        fields = ['first_name', 'last_name', 'email']
