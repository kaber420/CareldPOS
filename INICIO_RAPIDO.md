# Guía de Inicio Rápido

## Backend (FastAPI)

```bash
# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Copiar configuración
cp .env.example .env

# Ejecutar servidor (usa el puerto de tu .env automáticamente)
python run.py
```

Accede a: http://localhost:8100/docs

## Frontend (Svelte)

```bash
cd frontend

# Instalar dependencias
npm install

# Desarrollo (con proxy al backend)
npm run dev

# Build para producción
npm run build
```

## Deploy a SBC (RK3318)

### Opción 1: Servir frontend desde FastAPI

```bash
# En tu PC
cd frontend
npm install
npm run build
cp -r dist/* ../app/static/

# En la SBC
python run.py
```

### Opción 2: Frontend separado

```bash
# Frontend en la SBC
scp -r frontend/dist/* user@sbc:/var/www/pos-frontend/

# Configurar Nginx en la SBC
server {
    listen 80;
    server_name tu-dominio;

    location / {
        root /var/www/pos-frontend;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://localhost:8100;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Primeros Pasos

### 1. Crear usuario admin

```bash
curl -X POST http://localhost:8100/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@taller.com",
    "full_name": "Administrador",
    "password": "admin123",
    "role": "admin"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8100/api/v1/auth/login \
  -d "username=admin&password=admin123"
```

### 3. Acceder al frontend

Abre http://localhost:5173 (desarrollo) o http://localhost:8100 (producción)

## Estructura de Carpetas

```
fastapi_auth_app/
├── app/                    # Backend FastAPI
│   ├── api/               # Endpoints
│   ├── models/            # Modelos BD
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Lógica negocio
│   └── core/              # Seguridad, deps
├── frontend/              # Frontend Svelte
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   └── stores/
│   └── dist/              # Build output
├── static/                # Archivos estáticos
├── .env                   # Configuración
└── requirements.txt       # Python deps
```

## Endpoints Principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Registrar usuario |
| POST | `/api/v1/auth/login` | Login |
| GET | `/api/v1/users/me` | Perfil actual |
| GET | `/api/v1/customers/` | Listar clientes |
| POST | `/api/v1/customers/` | Crear cliente |
| GET | `/api/v1/devices/` | Listar dispositivos |
| POST | `/api/v1/repairs/` | Crear reparación |
| GET | `/api/v1/inventory/` | Listar inventario |
| POST | `/api/v1/payments/` | Registrar pago |

## Configuración (.env)

```env
# Seguridad - CAMBIAR EN PRODUCCIÓN
SECRET_KEY=tu-clave-secreta-muy-larga-y-segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Base de datos
DATABASE_URL=sqlite:///./data/repair_shop.db
PORT=8100

# CORS (para frontend separado)
CORS_ORIGINS=["http://localhost:5173","http://localhost:8100"]
```
