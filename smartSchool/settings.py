from pathlib import Path
import os
from dotenv import load_dotenv
import os
import dj_database_url

load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-v88^yqsum^*z&377a$i)szm=6b7$syjctu&_c5xpeo35#t)t1y'
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Force collectstatic to always include custom static dirs on Render
if not DEBUG:
    STATICFILES_FINDERS = [
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    ]

ALLOWED_HOSTS = ['.onrender.com', 'localhost', '127.0.0.1']

# ADD THESE 3 LINES AT THE END OF settings.py
LOGIN_URL = 'login'
# LOGIN_REDIRECT_URL = 'staff_dashboard'  # or 'student_dashboard'
# LOGIN_REDIRECT_URL = 'teacher_dashboard'  # or 'student_dashboard'
LOGOUT_REDIRECT_URL = 'login'

# ========================================
# TIME ZONE (Cambodia)
# ========================================
TIME_ZONE = 'Asia/Phnom_Penh'

# ========================================
# APPLICATION DEFINITION
# ========================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Your apps
    'users',
    'core',
    'academics',
    'attendance',
    'student',
    'reports',
    'notifications',
    'timetable',

    # Third-party
    'django_bootstrap5',
    'crispy_forms',
    'crispy_bootstrap5',
    'import_export',
    'channels',
    'chat',
    'ai_assistant',
]

# ========================================
# MIDDLEWARE
# ========================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'smartSchool.urls'

# ========================================
# TEMPLATES
# ========================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'smartSchool.wsgi.application'
ASGI_APPLICATION = 'smartSchool.asgi.application'



# Channel Layers for Django Channels (real-time chat)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}


# ========================================
# DATABASE
# ========================================
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3'),
        conn_max_age=600
    )
}

# ========================================
# CUSTOM USER MODEL
# ========================================
AUTH_USER_MODEL = 'users.CustomUser'

# ========================================
# PASSWORD VALIDATION
# ========================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ========================================
# INTERNATIONALIZATION
# ========================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'  # or your country
USE_I18N = True
USE_TZ = True

# ========================================
# STATIC FILES (CSS, JavaScript, Images)
# ========================================
STATIC_URL = '/static/'

# This is where collectstatic puts files (REQUIRED for production & collectstatic command)
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Your custom static folder (where you put css/js/images)
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATICFILES_DIRS += [BASE_DIR / 'static/css']

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ========================================
# MEDIA FILES (Uploaded photos, Excel, PDFs, etc.)
# ========================================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ========================================
# CRISPY FORMS
# ========================================
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# ========================================
# DEFAULT PRIMARY KEY
# ========================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# ========================================
# Part AI Assistant
# ========================================
# Get OpenAI API key safely from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")