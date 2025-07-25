# myproject/secret_settings.py

SECRET_KEY = 'django-insecure-*e8=pc7i(d#tfjnedlaqg(4s_(1+^9xnroohk69jjc5g717*r9'
DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}

# Други чувствителни настройки (ако има)