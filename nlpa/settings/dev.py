from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '8j)$i*7=q0!=tul=n^ug#gl-2ir&rw2)gr*yu)e5^eiiu0($_q'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


STRIPE_PUBLISHABLE_KEY = 'pk_test_51IUFQmIyfIE0cGLT4tEHeLbn31247AnPgB2GZllvhbZAKZ0s0vUZsTjXn9EVR4XNdlXwQh1aTlvaXCM2anDxffeF008gTb6r3y'
STRIPE_SECRET_KEY = 'sk_test_51IUFQmIyfIE0cGLTvNmGC7fWX3xuvnaTuXWu8Bndi7AhKvKjutDs5Fgb6CshG9jjJzLXAoOCE9Y4ZWHGm1mePW2s007sOLku4X'



try:
    from .local import *
except ImportError:
    pass
