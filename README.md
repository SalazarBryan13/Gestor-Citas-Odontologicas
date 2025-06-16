# Gestor de Citas Odontológicas

Sistema simple para gestionar citas odontológicas desarrollado con FastAPI, Jinja2 y Bootstrap.

## Características

- Agendar nuevas citas
- Ver lista de citas programadas
- Eliminar citas
- Interfaz responsiva con Bootstrap
- Almacenamiento en SQLite

## Requisitos

- Python 3.7 o superior
- pip (gestor de paquetes de Python)

## Instalación

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
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

## Uso

1. Iniciar el servidor:
```bash
python main.py
```

2. Abrir el navegador y acceder a:
```
http://localhost:8000
```

## Estructura del Proyecto

```
gestor-citas-medicas/
├── main.py              # Aplicación principal
├── requirements.txt     # Dependencias
├── citas.db            # Base de datos SQLite
└── templates/          # Plantillas HTML
    ├── base.html
    ├── index.html
    ├── citas.html
    └── nueva_cita.html
```

## Estructura de Ramas

- `main`: Código en producción
- `develop`: Integración de nuevas funcionalidades
- `feature/*`: Desarrollo de nuevas características
- `bugfix/*`: Corrección de errores
- `hotfix/*`: Arreglos urgentes en producción
- `release/*`: Preparación de versiones para producción 