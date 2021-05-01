from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '8j)$i*7=q0!=tul=n^ug#gl-2ir&rw2)gr*yu)e5^eiiu0($_q'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*']

SERVER_EMAIL='tim@onlandscape.co.uk'
DEFAULT_FROM_EMAIL='tim@onlandscape.co.uk'
EMAIL_MAIN=SERVER_EMAIL

STRIPE_PUBLISHABLE_KEY = 'pk_test_51IUFQmIyfIE0cGLT4tEHeLbn31247AnPgB2GZllvhbZAKZ0s0vUZsTjXn9EVR4XNdlXwQh1aTlvaXCM2anDxffeF008gTb6r3y'
STRIPE_SECRET_KEY = 'sk_test_51IUFQmIyfIE0cGLTvNmGC7fWX3xuvnaTuXWu8Bndi7AhKvKjutDs5Fgb6CshG9jjJzLXAoOCE9Y4ZWHGm1mePW2s007sOLku4X'


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mandrillapp.com'
EMAIL_USE_TLS = True
EMAIL_USE_SSH = False
EMAIL_PORT = 587
EMAIL_HOST_USER = 'onlandscape'
EMAIL_HOST_PASSWORD = 'b09fb401-6fb3-41b7-aff2-413c36f542a0'

#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_HOST = 'smtp.gmail.com'
#EMAIL_USE_TLS = True
#EMAIL_USE_SSH = False
#EMAIL_PORT = 587
#EMAIL_HOST_USER = 'admin@timparkin.co.uk'
#EMAIL_HOST_PASSWORD = 'fjweccuovxsmzzmw'
#DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


try:
    from .local import *
except ImportError:
    pass
