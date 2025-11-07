import os
from pathlib import Path

# No necesitamos dj_database_url si configuramos manualmente la DB.
# Comentar o eliminar esta línea:
# import dj_database_url
from dotenv import load_dotenv

load_dotenv() # Carga las variables del archivo .env al inicio

# Carga configuración base

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-lxefadkc!-zc)77fe(1*sru!aw83dhh6+zb$bfz+367%9mzbp*'

# SECURITY WARNING: don't run with debug turned on in production!
# Carga DEBUG desde variable de entorno. Por defecto 'True' para desarrollo.
# Se espera que en .env tengas DJANGO_DEBUG=True o DJANGO_DEBUG=False
DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() == 'true'



# --- Configuración de la Base de Datos para PostgreSQL LOCAL ---
# Leyendo variables separadas del .env como lo quieres
# Configuración de la base de datos
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DATABASE_ENGINE'),
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST'),
        'PORT': os.getenv('DATABASE_PORT'),
    }
}

# Eliminar o comentar estas líneas si tu PostgreSQL local no usa SSL
# Ya que estas son las que causan problemas en desarrollo si no tienes SSL configurado.
# DATABASES['default']['OPTIONS'] = {
#     'sslmode': 'require'
# }


STATIC_URL = '/static/assets/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# --- Hosts permitidos para desarrollo local y producción ---
# Permite localhost y 127.0.0.1 para desarrollo.
# En producción, solo debería contener los dominios de tu sitio web/API.
import os

ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1,10.10.11.41').split(',')

APPEND_SLASH=False # Mantén esto si tus rutas de frontend no esperan un slash al final.

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'drf_yasg',
    'rest_framework',
    'corsheaders', # Asegúrate de que esté aquí para CORS
    'clientes',
    'tipoVehiculo',
    'tipoCombustible',
    'vehiculos',	
    'marca',
    'tipo_pago',
    'trasmision',
    'seguridad',
    'costos',
    'vendedores',
    'contratos',
    'presupuesto',
    'pagoCuotas',
    'detallePagoCuotas',
    'generarCuotas',
    'creditos',
    
       
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware' # Asegúrate de que esté lo más alto posible
]

# --- Configuración de CORS para desarrollo local ---
# CORS_ORIGIN_ALLOW_ALL debe ser False para que CORS_ALLOWED_ORIGINS funcione.
# Solo pon True en desarrollo si no quieres restricciones. Para PROD, SIEMPRE FALSE.
CORS_ORIGIN_ALLOW_ALL = True # <--- ¡IMPORTANTE: Cambiado a False!
CORS_ALLOW_CREDENTIALS = True # Permite que el frontend envíe cookies/autenticación

# Lista explícita de orígenes permitidos para tu frontend local de Vue
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",    # El puerto donde corre tu frontend Vue en desarrollo
    "http://127.0.0.1:5173",    # La dirección loopback también para mayor compatibilidad
    "http://10.10.11.41:5173"
    # Si tu frontend de Vue corre en otro puerto local (ej. 3000, 8080), ajústalo aquí.
]

# Elimina o comenta las listas que ya no tienen efecto o no son el método principal
CORS_ORIGIN_ALLOW_WHITELIST = [] # Limpiado
CORS_ORIGIN_REGEX_WHITELIST = [] # Limpiado


ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'es-es'

#USE_I18N = True
#USE_L10N = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/assets/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'assets'),
)
MEDIA_URL='/uploads/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'uploads')


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

