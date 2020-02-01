"""
Django settings for stringkeeper project.

Generated by 'django-admin startproject' using Django 2.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/

https://www.youtube.com/watch?v=CTywsY6RvqI
apt install python3-pip python3-dev libpq-dev mysql-server libmysqlclient-dev nginx curl python3-widgetsnbextension python3-testresources build-essential dpkg-dev net-tools git nano gedit cmake curl wget dpkg-dev gdebi aptitude apt-transport-https ca-certificates software-properties-common -y

mysql_secure_installation


mysql -u root -p


CREATE DATABASE stringkeeper CHARACTER SET UTF8;
CREATE USER root@localhost IDENTIFIED BY 'r00t@str1ngk33p3r';
GRANT ALL PRIVILEGES ON stringkeeper.* TO root@localhost;
FLUSH PRIVILEGES;
exit

sudo -H pip3 install --upgrade pip
sudo -H pip3 install virtualenv

mkdir ~/myprojectdir ; cd ~/myprojectdir
virtualenv myprojectenv
source myprojectenv/bin/activate

pip install django gunicorn mysqlclient

django-admin.py startproject myproject ~/myprojectdir

gedit ~/myprojectdir/myproject/settings.py &>/dev/null
ALLOWED_HOSTS = ['*']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'myproject',
        'USER': 'myprojectuser',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '',
    }
}
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

~/myprojectdir/manage.py check
~/myprojectdir/manage.py makemigrations
~/myprojectdir/manage.py migrate
~/myprojectdir/manage.py createsuperuser
~/myprojectdir/manage.py collectstatic

~/myprojectdir/manage.py runserver 127.0.0.1:8000
http://127.0.0.1:8000/

cd ~/myprojectdir
gunicorn --bind 127.0.0.1:8000 myproject.wsgi
deactivate

gedit /etc/systemd/system/gunicorn.socket &>/dev/null
[unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target

gedit /etc/systemd/system/gunicorn.service &>/dev/null
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/root/myprojectdir
ExecStart=/root/myprojectdir/myprojectenv/bin/gunicorn \
    --access-logfile - \
    --workers 3 \
    --bind unix:/run/gunicorn.sock \
    myproject.wsgi:application

[Install]
WantedBy=multi-user.target

systemctl daemon-reload ; systemctl start gunicorn.socket ; systemctl enable gunicorn.socket

gedit /etc/nginx/sites-available/myproject &>/dev/null
server {
    listen 80;
    server_name 127.0.0.1;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /root/myprojectdir;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}

ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled
nginx -t

systemctl daemon-reload

systemctl restart gunicorn.socket gunicorn.service nginx.service ; systemctl status gunicorn.socket gunicorn.service nginx.service

http://127.0.0.1



amazon aurora postgresql
aurora postgresql 10.7
stringkeeper-django-mysql
root
r00tp0strgr3sqlstr1ngk33p3r

"""

import os
import socket
import debug_toolbar
from .standalone_tools import *
from django.core.exceptions import ImproperlyConfigured

import logging

logging.basicConfig(level=logging.CRITICAL)

# CRITICAL
# ERROR
# WARNING
# INFO
# DEBUG
# NOTSET


# from django.contrib.auth.models import User
# SECRET_KEY

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
eventlog('BASE_DIR: ' + str(BASE_DIR))
BASE_URL = ''

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '89y+eudf0eoqxck3bk4=$c5#l#b7j2i4y0!k)5dta7qu-dy3ir'


#amazon aws
#django-storages documentation 
AWS_ACCESS_KEY_ID='AKIAYZ2XE524MPVCJFBQ'
AWS_SECRET_ACCESS_KEY='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'
AWS_STORAGE_BUCKET_NAME='stringkeeper-django-static'
AWS_S3_REGION_NAME = 'us-west-2'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

#https://docs.aws.amazon.com/AmazonS3/latest/dev/acl-overview.html#canned-acl
AWS_DEFAULT_ACL = 'private'

from stringkeeper.aws.conf import *



# def test_stringkeeper(self):
#     #blackmesanetwork.com
#     to_email = 'andredoumad@gmail.com'
#     EMAIL_ADDRESS = 'AKIAYZ2XE524ITIKU2R2'
#     EMAIL_PASSWORD = 'BOdXu8OSHD16twbYZZLElgtFh/3QH/aadSIp6y9oQiSI'

#     msg = EmailMessage()
#     msg['Subject'] = 'Test subject line'
#     msg['From'] = 'andre@stringkeeper.com'
#     msg['To'] = to_email
#     msg.set_content('test msg content')

#     with smtplib.SMTP('email-smtp.us-west-2.amazonaws.com', 587) as smtp:
#         smtp.starttls()
#         smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
#         smtp.send_message(msg)


#Amazon SES
EMAIL_HOST = 'email-smtp.us-west-2.amazonaws.com'
EMAIL_HOST_USER = 'AKIAYZ2XE524ITIKU2R2' # gmail
EMAIL_HOST_PASSWORD = 'BOdXu8OSHD16twbYZZLElgtFh/3QH/aadSIp6y9oQiSI'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'Stringkeeper <andre@stringkeeper.com>'


# GMAIL
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_HOST_USER = 'andre@stringkeeper.com' # gmail
# EMAIL_HOST_PASSWORD = '!Tufankji1124'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# DEFAULT_FROM_EMAIL = 'Stringkeeper <andre@stringkeeper.com>'

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
    'debug_toolbar',
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
    'core',
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
    'debug_toolbar.middleware.DebugToolbarMiddleware',
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
        
        #standard localhost settings
        #'ENGINE': 'django.db.backends.mysql',
        #'NAME': 'stringkeeper',
        #'USER': 'root',
        #'PASSWORD': 'r00t@str1ngk33p3r',
        #'HOST': 'localhost',
        #'PORT': '',
        
        
        #local postgre settings
        #'ENGINE': 'django.db.backends.postgresql',
        #'NAME': 'stringkeeper',
        #'USER': 'root',
        #'PASSWORD': 'r00tp0strgr3sqlstr1ngk33p3r',
        #'HOST': 'localhost',
        #'PORT': '5432',
        

        #amazon rds postgre settings
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'stringkeeper',
        'USER': 'root',
        'PASSWORD': 'r00tp0strgr3sqlstr1ngk33p3r',
        'HOST': 'stringkeeper.c23mwd8ntiyq.us-west-2.rds.amazonaws.com',
        'PORT': '5432',

        #'ENGINE': 'django.db.backends.sqlite3',
        #'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
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



ASGI_APPLICATION = 'chat.routing.application'

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




# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

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
    # SESSION_COOKIE_SECURE=True
    # SESSION_COOKIE_HTTPONLY=True
    # SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')
    # SECURE_SSL_REDIRECT = True

    eventlog('log filepath: ' + str(os.path.join(BASE_DIR, 'stringkeeperremotedebug.txt')) )
    f = open(str(os.path.join(BASE_DIR, 'stringkeeperremotedebug.txt')), "w")
    f.write("")
    f.close()
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'file': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filename': os.path.join(BASE_DIR, 'stringkeeperremotedebug.txt'),
            },
        },
        'loggers': {
            'django': {
                'handlers': ['file'],
                'level': 'DEBUG',
                'propagate': True,
            },
        },
    }

    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            # 'BACKEND': 'asgiref.inmemory.ChannelLayer',
            'CONFIG': {
                "hosts": [('www.stringkeeper.com', 6379)],
                # "hosts": [('44.225.82.162', 6379)],
                # "hosts": [('127.0.0.1', 5432)],
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



    '''
    CORS_REPLACE_HTTPS_REFERER      = False
    HOST_SCHEME                     = "http://"
    SECURE_PROXY_SSL_HEADER         = None
    SECURE_SSL_REDIRECT             = False
    SESSION_COOKIE_SECURE           = False
    CSRF_COOKIE_SECURE              = False
    SECURE_HSTS_SECONDS             = None
    SECURE_HSTS_INCLUDE_SUBDOMAINS  = False
    SECURE_FRAME_DENY               = False
    '''
    eventlog('log filepath: ' + str(os.path.join(BASE_DIR, 'stringkeeperlocaldebug.log')) )
    f = open(str(os.path.join(BASE_DIR, 'stringkeeperlocaldebug.log')), "w")
    f.write("")
    f.close()
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
        },
    }

    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                "hosts": [('www.stringkeeper.com', 6379)],
                # "hosts": [('44.225.82.162', 6379)],
                # "hosts": [('127.0.0.1', 5432)],
            },
        },
    }
    #https://django-debug-toolbar.readthedocs.io/en/latest/installation.html
    

#STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'