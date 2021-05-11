from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True



# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*']

SERVER_EMAIL='info@naturallandscapeawards.com'
DEFAULT_FROM_EMAIL='info@naturallandscapeawards.com'
EMAIL_MAIN=SERVER_EMAIL


try:
    from .local import *
except ImportError:
    pass
