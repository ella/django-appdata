DEBUG = True

ROOT_URLCONF = 'test_app_data.urls'
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

TEMPLATE_LOADERS = (
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_OPTIONS = {
    'context_processors': [],
    'loaders': TEMPLATE_LOADERS,
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'OPTIONS': TEMPLATE_OPTIONS
    },
]

SECRET_KEY = 'very-secret'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/tmp/app_data.db',
    }
}

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',

    'test_app_data',
)
