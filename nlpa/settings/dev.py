from .base import *
import os


ADMINS = [('Tim Parkin', 'info@timparkin.co.uk'), ]



# SECURITY WARNING: define the correct hosts in production!

SERVER_EMAIL='info@naturallandscapeawards.com'
DEFAULT_FROM_EMAIL='info@naturallandscapeawards.com'
EMAIL_MAIN=SERVER_EMAIL


try:
    from .local import *
except ImportError:
    pass
