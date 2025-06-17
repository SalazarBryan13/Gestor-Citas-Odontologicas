# Gestor de Citas Odontológicas

Sistema simple para gestionar citas odontológicas desarrollado con FastAPI, Jinja2 y Bootstrap.

## 🚀 Características

* Agendar nuevas citas
* Ver lista de citas programadas
* Eliminar citas
* Interfaz responsiva con Bootstrap
* Almacenamiento en SQLite
* Contenedorización con Docker
* Sistema de autenticación
* Notificaciones de citas

## 📋 Requisitos

### Desarrollo Local
* Python 3.11 o superior
* pip (gestor de paquetes de Python)

### Docker
* Docker Engine
* Docker Compose (opcional)

## 🚀 Instalación

### Método 1: Desarrollo Local

1. Clonar el repositorio:
```bash
git clone https://github.com/SalazarBryan13/Gestor-Citas-Odontologicas.git
cd gestor-citas-medicas
```

2. Crear un entorno virtual (opcional pero recomendado):
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Inicializar la base de datos:
```bash
python src/init_db.py
```

### Método 2: Usando Docker

1. Construir la imagen:
```bash
docker build -t bryanhert/gestor-citas-medicas:latest .
```

2. Ejecutar el contenedor:
```bash
docker run -p 8000:8000 -v $(pwd)/data:/app/data bryanhert/gestor-citas-medicas:latest
```

O usar la imagen directamente desde Docker Hub:
```bash
docker pull bryanhert/gestor-citas-medicas:latest
docker run -p 8000:8000 -v $(pwd)/data:/app/data bryanhert/gestor-citas-medicas:latest
```

## 💻 Uso

### Desarrollo Local

1. Iniciar el servidor:
```bash
python src/main.py
```

2. Abrir el navegador y acceder a:
```
http://localhost:8000
```

### Docker

La aplicación estará disponible en:
```
http://localhost:8000
```

## 📁 Estructura del Proyecto

```
gestor-citas-medicas/
├── src/                # Código fuente de la aplicación
│   ├── __init__.py
│   ├── main.py        # Aplicación principal
│   ├── auth.py        # Autenticación
│   ├── db.py          # Base de datos
│   ├── notificaciones.py
│   ├── init_db.py
│   └── create_test_user.py
├── routers/           # Rutas de la API
│   └── citas.py
├── data/              # Datos de la aplicación
│   └── citas.db       # Base de datos SQLite
├── templates/         # Plantillas HTML
│   ├── base.html
│   ├── index.html
│   ├── citas.html
│   └── nueva_cita.html
├── static/           # Archivos estáticos
├── tests/           # Pruebas
├── requirements.txt  # Dependencias
├── Dockerfile       # Configuración de Docker
├── .flake8         # Configuración de Flake8
├── pytest.ini      # Configuración de Pytest
└── README.md        # Este archivo
```

## 🌿 Estructura de Ramas

* `main`: Código en producción
* `develop`: Integración de nuevas funcionalidades
* `feature/*`: Desarrollo de nuevas características
* `bugfix/*`: Corrección de errores
* `hotfix/*`: Arreglos urgentes en producción
* `release/*`: Preparación de versiones para producción

## 🐳 Docker Hub

La imagen Docker está disponible en Docker Hub:
```bash
docker pull bryanhert/gestor-citas-medicas:latest
```

## 🛠️ Desarrollo

### Pruebas
Para ejecutar las pruebas:
```bash
pytest
```

### Linting
Para verificar el estilo del código:
```bash
flake8 src tests
```

## 👥 Contribución

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request



