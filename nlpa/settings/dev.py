from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '***REMOVED***'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


STRIPE_PUBLISHABLE_KEY = 'pk_test_51IUFQmIyfIE0cGLT4tEHeLbn31247AnPgB2GZllvhbZAKZ0s0vUZsTjXn9EVR4XNdlXwQh1aTlvaXCM2anDxffeF008gTb6r3y'
STRIPE_SECRET_KEY = '***REMOVED***'



try:
    from .local import *
except ImportError:
    pass
