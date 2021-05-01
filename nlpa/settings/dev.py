from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True



# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*']

SERVER_EMAIL='tim@onlandscape.co.uk'
DEFAULT_FROM_EMAIL='tim@onlandscape.co.uk'
EMAIL_MAIN=SERVER_EMAIL


try:
    from .local import *
except ImportError:
    pass
