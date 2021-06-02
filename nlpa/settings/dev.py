from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ADMINS = [('Tim Parkin', 'info@timparkin.co.uk'), ]



# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['submit.naturallandscapeawards.com']

SERVER_EMAIL='info@naturallandscapeawards.com'
DEFAULT_FROM_EMAIL='info@naturallandscapeawards.com'
EMAIL_MAIN=SERVER_EMAIL


try:
    from .local import *
except ImportError:
    pass


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/www/submit.naturallandscapeawards.com/NLPA-Submissions/nlpa-filehandler.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers':['file'],
            'propagate': True,
            'level':'DEBUG',
        },
        'MYAPP': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    }
}
