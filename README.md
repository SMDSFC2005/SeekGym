# SeekGym

Aplicación web para consultar el estado de ocupación de gimnasios y descubrir la mejor hora para entrenar sin colas ni esperas.

## Tecnologías

- **Backend**: Django 6 + Django REST Framework + JWT (simplejwt)
- **Frontend**: Vue 3 + Vite + Pinia + Vue Router
- **Base de datos**: SQLite (incluida, no requiere configuración extra)

## Requisitos previos

- Python 3.11 o superior
- Node.js 18 o superior
- pip

---

## Puesta en marcha

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd SeekGym
```

### 2. Backend

```bash
cd backend
```

#### Crear y activar el entorno virtual

```bash
# Windows
python -m venv entorno
entorno\Scripts\activate

# Linux / macOS
python -m venv entorno
source entorno/bin/activate
```

#### Instalar dependencias

```bash
pip install -r requirements.txt
```

#### Configurar variables de entorno

Copia el archivo de ejemplo y edítalo:

```bash
cp .env.example .env
```

Abre `.env` y cambia `SECRET_KEY` por cualquier cadena larga y aleatoria. Para desarrollo puedes dejarlo como está.

#### Aplicar migraciones

```bash
python manage.py migrate
```

#### Cargar datos iniciales

```bash
# Provincias y municipios de España
python manage.py seed_locations

# Datos de ocupación de ejemplo para los gimnasios de prueba
python manage.py seed_occupancy
```

#### Crear superusuario (opcional, para acceder al panel de admin)

```bash
python manage.py createsuperuser
```

#### Arrancar el servidor de desarrollo

```bash
python manage.py runserver
```

El backend queda disponible en `http://localhost:8000`.

---

### 3. Frontend

Abre una nueva terminal desde la raíz del proyecto:

```bash
cd frontend
npm install
npm run dev
```

El frontend queda disponible en `http://localhost:5173`.

---

## Funcionalidades implementadas

### Autenticación y roles
- Registro e inicio de sesión con JWT
- Tres roles: **Usuario normal**, **Propietario de gimnasio** (requiere aprobación del admin) y **Superusuario**
- Página de perfil con badge de rol

### Gimnasios
- Listado de gimnasios con búsqueda por nombre y filtros por provincia y municipio
- Vista de detalle con imagen, descripción, precio y horario
- Creación y edición de gimnasio (solo propietarios aprobados y superusuarios)
- Eliminación de gimnasio (propietario o superusuario)

### Ocupación y recomendaciones
- **Ocupación actual**: porcentaje en tiempo real ajustado por hora, día, festivos y meses
- **Mejor hora hoy**: franja con menor ocupación prevista para el resto del día
- **Mejor hora mañana**: predicción para el día siguiente
- **Timeline del día**: gráfico de barras con la ocupación hora a hora
- Ajustes especiales: última hora antes del cierre, festivos nacionales, Carnaval, Semana Santa, Nochebuena, Nochevieja, etc.

### Social
- Seguir / dejar de seguir gimnasios
- Vista "Mis seguidos" con los gimnasios seguidos
- Notificaciones de nuevos anuncios de los gimnasios seguidos

### Panel de administración
- Aprobación y rechazo de solicitudes de cuenta tipo gimnasio
- Badge con número de solicitudes pendientes en el campana de notificaciones

### Publicaciones del gimnasio
- Los propietarios pueden publicar promociones, ofertas y novedades
- Los seguidores reciben notificación de nuevas publicaciones

---

## Cómo comprobar las funcionalidades

1. **Registro normal**: ve a `/register`, crea una cuenta de tipo "Usuario" y entra en `/home`.
2. **Registro de gimnasio**: crea una cuenta de tipo "Gimnasio". Verás que está pendiente. Con el superusuario, apruébala desde la campana → "Ver solicitudes".
3. **Crear un gimnasio**: con la cuenta de gimnasio aprobada, usa el botón "Crear mi gimnasio".
4. **Ocupación**: entra al detalle de cualquier gimnasio con datos de ocupación para ver el estado actual, la mejor hora de hoy y la de mañana.
5. **Seguir**: usa el botón "+" en las tarjetas del home o el botón "Seguir" en el detalle.
6. **Búsqueda**: escribe en la barra de búsqueda del home para filtrar por nombre en tiempo real.

---

## Estructura del proyecto

```
SeekGym/
├── backend/
│   ├── config/          # Configuración de Django (settings, urls, wsgi)
│   ├── users/           # App de usuarios y autenticación
│   ├── gyms/            # App principal: gimnasios, ocupación, horarios
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── services/
│   │   │   ├── occupancy.py   # Lógica de cálculo de ocupación y recomendaciones
│   │   │   └── profile_seed.py
│   │   └── management/commands/
│   │       ├── seed_locations.py  # Provincias y municipios
│   │       └── seed_occupancy.py  # Datos de ocupación de prueba
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── features/
│   │   │   ├── auth/    # Login, registro, perfil
│   │   │   ├── gyms/    # Home, detalle, crear, seguidos
│   │   │   └── admin/   # Panel de solicitudes
│   │   ├── router/
│   │   └── stores/
│   └── package.json
└── README.md
```
