from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    change_form_template = 'loginas/change_form.html'
    add_form = UserCreationForm
    form = UserChangeForm
    model = CustomUser
    list_display = ['pk', 'email', 'username', 'first_name', 'last_name', 'date_of_birth', 'payment_status','payment_plan']
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('email', 'first_name', 'last_name', 'display_name', 'date_of_birth', 'address1', 'address2', 'zip_code', 'city', 'country', 'mobile_phone', 'additional_information', 'photo','payment_status','payment_plan')}),
    )
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('display_name', 'date_of_birth', 'address1', 'address2', 'zip_code', 'city', 'country', 'mobile_phone', 'additional_information', 'photo','payment_status','payment_plan')}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
