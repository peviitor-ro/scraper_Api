"""
Django settings for scraper_Api project.

Generated by 'django-admin startproject' using Django 4.0.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
import os
import platform

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-nh-rh#j35y9n9o11$h@vto$^#5gr73f!0&wqml_1g!n_d(5%&g'

# SECURITY WARNING: don't run with debug turned on in production!
if platform.system() == 'Darwin' or platform.system() == 'windows':
    DEBUG = True
else:
    DEBUG = False

APPEND_SLASH = False

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'dev.laurentiumarian.ro',
    'api.laurentiumarian.ro',
]

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'https://dev.laurentiumarian.ro',
    'https://api.laurentiumarian.ro',

]

# Default Timeout
DEFAULT_TIMEOUT = 60 * 5

# Cors
CORS_ALLOWED_ORIGINS = (
    'http://localhost:8000',
    'https://dev.laurentiumarian.ro',
    'http://127.0.0.1:5500',
    'http://localhost:5500',
    'https://scraper-ui.netlify.app',
    'https://scrapers.peviitor.ro',
    'https://api.laurentiumarian.ro',
)
CORS_ALLOW_HEADERS = ('*')
CORS_ALLOW_METHODS = ['GET', 'POST']
CORS_ALLOW_CREDENTIALS = True

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Api
    'rest_framework',
    'rest_framework.authtoken',
    'oauth2_provider',
    'social_django',
    'drf_social_oauth2',

    # Cors
    'corsheaders',

    # Apps
    'Api',
    'validator',

]

MIDDLEWARE = [
    # Cors
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    
    # Github
    'social_django.middleware.SocialAuthExceptionMiddleware'
]

ROOT_URLCONF = 'scraper_Api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR, os.path.join(BASE_DIR, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                # OAuth2
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'scraper_Api.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join('root')
STATICFILES_DIRS = (os.path.join('static/'), )

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# OAUTH2
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # OAuth
        'drf_social_oauth2.authentication.SocialAuthentication',

        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

AUTHENTICATION_BACKENDS = (
    # Others auth providers (e.g. Facebook, OpenId, etc)

    # GitHub OAuth2
    'social_core.backends.github.GithubOAuth2',

    # Django
    'django.contrib.auth.backends.ModelBackend',

    # DRF Social OAuth2
    'drf_social_oauth2.backends.DjangoOAuth2',

)

LOGIN_URL = '/homepage/'
LOGIN_REDIRECT_URL = 'oauth:login'
LOGOUT_URL = '/logout'
LOGOUT_REDIRECT_URL = '/homepage/'

# SOCIAL_AUTH_GITHUB_KEY = 'c41a2e3f5b5c972a068c'
# SOCIAL_AUTH_GITHUB_SECRET = '479c50824f1e0c53eb24512859627e68cbbf270a'


SOCIAL_AUTH_GITHUB_KEY = '0b9196806bf773e4d68e'
SOCIAL_AUTH_GITHUB_SECRET = '28a229ef1e0ca4eb094f388149203dc55d481e7d'