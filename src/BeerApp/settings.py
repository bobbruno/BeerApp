"""
Django settings for BeerApp project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

#  Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from django.conf.global_settings import DEFAULT_INDEX_TABLESPACE, DEFAULT_TABLESPACE, \
    TEMPLATE_DIRS, STATICFILES_DIRS
import os


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates'),
                 os.path.join(BASE_DIR, 'BeerNav/templates')]
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)


#  Quick-start development settings - unsuitable for production
#  See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

#  SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '&r&95u$h!ulno5@fs#raal&@g70#$#ylq-b1#vms@@8uj&jbhl'

#  SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


#  Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'allaccess',
    'BeerNav',
    'floppyforms'
)

AUTHENTICATION_BACKENDS = (
    #  Default backend
    'django.contrib.auth.backends.ModelBackend',
    #  Additional backend
    'allaccess.backends.AuthorizedServiceBackend',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'BeerApp.urls'

WSGI_APPLICATION = 'BeerApp.wsgi.application'


#  Database
#  https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'BeerDb',
        'USER': 'django_beer',
        'PASSWORD': 'MyNextBeer',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

DEFAULT_INDEX_TABLESPACE = 'Beer_Ix'
DEFAULT_TABLESPACE = 'Beer_Data'

#  Internationalization
#  https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_L10N = True

USE_TZ = True

CHARSET = 'utf8'


#  Static files (CSS, JavaScript, Images)
#  https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
