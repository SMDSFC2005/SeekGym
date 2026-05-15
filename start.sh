#!/bin/bash
cd /app/backend

python manage.py migrate

python manage.py shell << 'EOF'
from users.models import Usuario
if not Usuario.objects.filter(username='Sergio').exists():
    Usuario.objects.create_superuser(username='Sergio', email='sergio@seekgym.com', password='12345678')
    print('Superusuario Sergio creado')
else:
    print('Superusuario Sergio ya existe')
EOF

gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 1
