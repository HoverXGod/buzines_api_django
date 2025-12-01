ALLOWED_HOSTS_LOCAL = ['*']
INSTALLED_APPS_LOCAL = [
    'debug_toolbar',
]
MIDDLEWARE_LOCAL = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    ]
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
    '0.0.0.0',
    
]

def get_local_db(BASE_DIR):
    return {
                'default': {
                    'ENGINE': 'django.db.backends.postgresql',
                    'NAME': 'main',
                    'USER': 'root',
                    'PASSWORD': 'root',
                    'HOST': 'db',  # Имя сервиса в docker-compose.yml
                    'PORT': '5432',
                }
            }

