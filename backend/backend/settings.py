import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv() # Carga las variables del archivo .env al inicio

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-lxefadkc!-zc)77fe(1*sru!aw83dhh6+zb$bfz+367%9mzbp*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() == 'true'

# --- Hosts permitidos ---
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1,10.10.11.41').split(',')

APPEND_SLASH=False

# --- Configuración de la Base de Datos ---
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

# --- Application definition ---

INSTALLED_APPS = [
    # Aplicaciones de Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Aplicaciones de Terceros
    'drf_yasg',
    'rest_framework',
    'corsheaders', # <-- CORRECCIÓN: Está en la lista
    
    # Tus Aplicaciones
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
    'reservas',
    'tipo_arriendo',
    'gastos',
    'informes',
    'auditoria',
]

# --- MIDDLEWARE ---
# ¡CORRECCIÓN: 'CorsMiddleware' está ahora en la posición correcta (cerca del inicio)!
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', # <-- PUESTO AQUÍ
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --- Configuración de CORS (Cross-Origin Resource Sharing) ---

# ¡CORRECCIÓN: Puesto en 'False' para permitir que 'CORS_ALLOW_CREDENTIALS' funcione!
CORS_ORIGIN_ALLOW_ALL = False 

# Permite que el frontend envíe cookies (como la de sesión de Django)
CORS_ALLOW_CREDENTIALS = False 

# Lista de orígenes (tu frontend) que tienen permiso para conectarse
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",    
    "http://127.0.0.1:5173",    
    "http://10.10.11.41:5173"
]

# Headers permitidos
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# (Configuraciones antiguas, las dejamos vacías para evitar conflictos)
CORS_ORIGIN_ALLOW_WHITELIST = [] 
CORS_ORIGIN_REGEX_WHITELIST = [] 


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

# --- Validación de Contraseñas ---
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

# --- Internacionalización ---
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Santiago'  # Zona horaria de Chile
USE_TZ = False  # Desactivar timezone-aware datetimes para evitar conversiones
#USE_I18N = True
#USE_L10N = True

# --- Archivos Estáticos y Media ---
STATIC_URL = '/assets/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'assets'),
)
MEDIA_URL='/uploads/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'uploads')

# --- Tipo de Clave Primaria ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'