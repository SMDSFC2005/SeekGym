import django, os, sys
sys.path.insert(0, '/app/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from users.models import Usuario
Usuario.objects.filter(username='Sergio').delete()
u = Usuario.objects.create_superuser(username='Sergio', email='sergio@seekgym.com', password='12345678')
print('Usuario creado:', u.username)
