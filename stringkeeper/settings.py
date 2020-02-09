import os

import socket
# import debug_toolbar
from .standalone_tools import *
from django.core.exceptions import ImproperlyConfigured

import logging

logging.basicConfig(level=logging.CRITICAL)


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
eventlog('BASE_DIR: ' + str(BASE_DIR))
BASE_URL = ''


# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = '89y+eudf0eoqxck3bk4=$c5#l#b7j2i4y0!k)5dta7qu-dy3ir' comprimised
SECRET_KEY = '89y+eXdf5eoqxak4bk4=$c5#l#B6j2i4!0!k)4dTa7qu-vy61r'

#amazon aws
#django-storages documentation 
# AWS_ACCESS_KEY_ID='AKIAYZ2XE524MPVCJFBQ'
AWS_ACCESS_KEY_ID= 'AKIAYZ2XE524BTQLO5XR'
# AWS_SECRET_ACCESS_KEY='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'
AWS_SECRET_ACCESS_KEY= 'NAyamthT5QfmSImbknbjlRVicC+2ICA3to50Ttnp'
AWS_STORAGE_BUCKET_NAME='stringkeeper-django-static'
AWS_S3_REGION_NAME = 'us-west-2'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

#https://docs.aws.amazon.com/AmazonS3/latest/dev/acl-overview.html#canned-acl
AWS_DEFAULT_ACL = 'private'

from stringkeeper.aws.conf import *



#Amazon SES
EMAIL_HOST = 'email-smtp.us-west-2.amazonaws.com'
# EMAIL_HOST_USER = 'AKIAYZ2XE524ITIKU2R2' # gmail
# EMAIL_HOST_PASSWORD = 'BOdXu8OSHD16twbYZZLElgtFh/3QH/aadSIp6y9oQiSI'
EMAIL_HOST_USER = 'AKIAYZ2XE524B2NTG7DI'
EMAIL_HOST_PASSWORD = 'BGJsy/NhlXE1x8HM8b6VGSuFXjwmfWmYYk5qntB0iwlw'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'Stringkeeper <andre@stringkeeper.com>'


DEFAULT_ACTIVATION_DAYS = 7


STATIC_URL = '/static/'

ALLOWED_HOSTS = ['www.stringkeeper.com', '*']

LOGIN_URL = '/login/'
LOGIN_URL_REDIRECT = '/'
LOGOUT_URL = '/logout/'
LOGOUT_REDIRECT_URL = '/login/'
ROOT_URLCONF = 'stringkeeper.urls'

# LOGIN_URL = '/login/'
# LOGIN_URL_REDIRECT = '/'
# LOGOUT_URL = '/logout/'

STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)

MEDIA_URL = '/mediafiles/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

# Application definition
# components
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'debug_toolbar',
    'blog',
    'storages',
    'subscription',
    'search',
    'tags',
    'carts',
    'marketing',
    'orders',
    'accounts',
    'analytics',
    'billing',
    'addresses',
    'webharvest',
    'chat',
    # 'core',
    'rest_framework',
    'channels',
]


AUTH_USER_MODEL = 'accounts.User' #changes the built in user model


FORCE_SESSION_TO_ONE = True
FORCE_INACTIVE_USER_ENDSESSION= True

STRIPE_BILLING_SERVICE = False

if STRIPE_BILLING_SERVICE == True:
    BRAINTREE_BILLING_SERVICE = False
else:
    BRAINTREE_BILLING_SERVICE = True

STRIPE_SECRET_KEY = 'sk_test_UQ6hFgP5OZ9KXeSWvO39jgTb0099ffMFNJ'
STRIPE_PUB_KEY = 'pk_test_k8LAxPXmWxonT6ZUDVxjsuzL00LCGJ2rLX'

BRAINTREE_PRODUCTION = False
BRAINTREE_ENVIRONMENT = 'sandbox'
BRAINTREE_MERCHANT_ID = 's7s9hk3y2frmyq6n'
BRAINTREE_PUBLIC_KEY = 'hnzpmswf3hqpzwtj'
BRAINTREE_PRIVATE_KEY = '888ebe7f91701688efdc1f9c52471b8f'

MAILCHIMP_API_KEY = "b1ac039ee89ff25296c78c3d3d6874b4-us4"
MAILCHIMP_DATA_CENTER = "us4"
MAILCHIMP_EMAIL_LIST_ID = "7d3e434d40"


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'stringkeeper.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'stringkeeper.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        

        #amazon rds postgre settings
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'stringkeeper',
        'USER': 'root',
        # 'PASSWORD': 'r00tp0strgr3sqlstr1ngk33p3r',
        'PASSWORD': 'r42tp0strgr2sqlstr1ngk47p365r',
        'HOST': 'stringkeeper.c23mwd8ntiyq.us-west-2.rds.amazonaws.com',
        'PORT': '5432',


    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]



ASGI_APPLICATION = 'stringkeeper.routing.application'

AUTH_PASSWORD_VALIDATORS = []

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny'
        # 'rest_framework.permissions.IsAuthenticated'
    ],
    'DEFAULT_PAGINATION_CLASS':
        'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100
}


MESSAGES_TO_LOAD = 15


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

INTERNAL_IPS = [
    # ...
    '127.0.0.1',
    # ...
]

if socket.gethostname()=="www.stringkeeper.com":
    eventlog ('running production mode')
    BASE_URL = 'https://www.stringkeeper.com'
    DEBUG = False
    # ssl
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE=True
    SESSION_COOKIE_HTTPONLY=True
    # SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')
    # SECURE_SSL_REDIRECT = True

    eventlog('log filepath: ' + str(os.path.join(BASE_DIR, 'stringkeeperremotedebug.log')) )
    f = open(str(os.path.join(BASE_DIR, 'stringkeeperremotedebug.log')), "w")
    f.write("")
    f.close()
    LOGGING_FILEPATH = str(os.path.join(BASE_DIR, 'stringkeeperremotedebug.log'))
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'file': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filename': os.path.join(BASE_DIR, 'stringkeeperremotedebug.log'),
            },
        },
        'loggers': {
            'django': {
                'handlers': ['file'],
                'level': 'DEBUG',
                'propagate': True,
            },
        # 'daphne': {
        #     'handlers': [
        #         'console',
        #     ],
        #     'level': 'DEBUG'
        # },
        },
    }

    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            # 'BACKEND': 'asgiref.inmemory.ChannelLayer',
            'CONFIG': {
                # "hosts": [('www.stringkeeper.com', 6379)],
                # "hosts": [('44.232.251.35', 6379)],
                #"hosts": [('127.0.0.1', 6729)],
                "hosts": [("redis://:Fzy5dDT2e6tlMNJ7GXyRGicCMbKxR60xHbigVcYFlw3cHW4dOxe7WfB9cFfdADF9jB9y3ajAIrcn5YdH@172.26.14.96:6379/0")],
            },
        },
    }

else:
    eventlog(' running non-production settings')
    eventlog(' --- !! REMEMBER !! ---')
    eventlog('USE A PRIVATE WINDOW IN CHROME')
    BASE_URL = 'http://127.0.0.1:8000'
    DEBUG = True
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE=False
    SESSION_COOKIE_HTTPONLY=False
    SECURE_PROXY_SSL_HEADER = None
    SECURE_SSL_REDIRECT = False

    eventlog('log filepath: ' + str(os.path.join(BASE_DIR, 'stringkeeperlocaldebug.log')) )
    f = open(str(os.path.join(BASE_DIR, 'stringkeeperlocaldebug.log')), "w")
    f.write("")
    f.close()
    LOGGING_FILEPATH = str(os.path.join(BASE_DIR, 'stringkeeperlocaldebug.log'))
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'file': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filename': os.path.join(BASE_DIR, 'stringkeeperlocaldebug.log'),
            },
        },
        'loggers': {
            'django': {
                'handlers': ['file'],
                'level': 'DEBUG',
                'propagate': True,
            },
            # 'daphne': {
            #     'handlers': [
            #         'console',
            #     ],
            #     'level': 'DEBUG'
            # },
        },
    }

    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                "hosts": [('localhost', 6379)],
                # "hosts": [("redis://:Fzy5dDT2e6tlMNJ7GXyRGicCMbKxR60xHbigVcYFlw3cHW4dOxe7WfB9cFfdADF9jB9y3ajAIrcn5YdH@44.233.102.110:6379/0")],
            },
        },
    }
    #https://django-debug-toolbar.readthedocs.io/en/latest/installation.html
    

#STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'