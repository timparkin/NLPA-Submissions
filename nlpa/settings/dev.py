from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '***REMOVED***'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*']

SERVER_EMAIL='tim@onlandscape.co.uk'
DEFAULT_FROM_EMAIL='tim@onlandscape.co.uk'
EMAIL_MAIN=SERVER_EMAIL

STRIPE_PUBLISHABLE_KEY = 'pk_test_51IUFQmIyfIE0cGLT4tEHeLbn31247AnPgB2GZllvhbZAKZ0s0vUZsTjXn9EVR4XNdlXwQh1aTlvaXCM2anDxffeF008gTb6r3y'
STRIPE_SECRET_KEY = '***REMOVED***'


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mandrillapp.com'
EMAIL_USE_TLS = True
EMAIL_USE_SSH = False
EMAIL_PORT = 587
EMAIL_HOST_USER = 'onlandscape'
EMAIL_HOST_PASSWORD = '***REMOVED***'

#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_HOST = 'smtp.gmail.com'
#EMAIL_USE_TLS = True
#EMAIL_USE_SSH = False
#EMAIL_PORT = 587
#EMAIL_HOST_USER = 'admin@timparkin.co.uk'
#EMAIL_HOST_PASSWORD = '***REMOVED***'
#DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


try:
    from .local import *
except ImportError:
    pass
