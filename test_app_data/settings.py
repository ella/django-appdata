DEBUG = True

ROOT_URLCONF = "test_app_data.urls"
STATIC_URL = "/static/"
MEDIA_URL = "/media/"

TEMPLATE_LOADERS = ("django.template.loaders.app_directories.Loader",)

TEMPLATE_OPTIONS = {
    "context_processors": [
        "django.contrib.auth.context_processors.auth",
        "django.template.context_processors.request",
        "django.contrib.messages.context_processors.messages",
    ],
    "loaders": TEMPLATE_LOADERS,
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "OPTIONS": TEMPLATE_OPTIONS,
    },
]

SECRET_KEY = "very-secret"

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}

MIDDLEWARE = (
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
)

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.admin",
    "django.contrib.messages",
    "test_app_data",
)
