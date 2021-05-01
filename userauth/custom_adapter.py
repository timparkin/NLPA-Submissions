from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings

class CustomAccountAdapter(DefaultAccountAdapter):
    def get_from_email(self):
        return settings.DEFAULT_FROM_EMAIL

