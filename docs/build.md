# Informe del Proceso de Build

## Introducción

En el presente informe se detalla el proceso de construcción (build) del proyecto Gestor de Citas Odontológicas. Este proceso es fundamental para asegurar que la aplicación pueda ser desplegada de manera consistente y confiable en diferentes entornos.

## Configuración del Build

### Dockerfile

El proceso de build se realiza mediante un Dockerfile, que define cómo se construye la imagen de la aplicación. El Dockerfile está estructurado en varias etapas para optimizar el tamaño final de la imagen y mejorar la seguridad:

```dockerfile
# Etapa de construcción
FROM python:3.11-slim as builder

WORKDIR /app

# Instalación de dependencias de construcción
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia de archivos de dependencias
COPY requirements.txt .

# Instalación de dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Etapa final
FROM python:3.11-slim

WORKDIR /app

# Copia de dependencias desde la etapa de construcción
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/

# Copia del código de la aplicación
COPY . .

# Exposición del puerto
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Workflow de Build (build.yml)

El proceso de build está automatizado mediante GitHub Actions, utilizando el archivo `build.yml`. Este workflow se encarga de:

1. **Preparación del Entorno**:
   - Checkout del código
   - Configuración de Docker Buildx
   - Login en GitHub Container Registry

2. **Construcción de la Imagen**:
   - Build de la imagen Docker
   - Etiquetado de la imagen
   - Push de la imagen al registro

3. **Publicación**:
   - Publicación de la imagen en GitHub Container Registry
   - Etiquetado de versiones

## Proceso de Construcción

### 1. Preparación del Entorno

El proceso comienza con la preparación del entorno de construcción:

```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v2

- name: Login to GitHub Container Registry
  uses: docker/login-action@v2
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

### 2. Construcción de la Imagen

La construcción de la imagen se realiza en varias etapas:

1. **Instalación de Dependencias**:
   - Se instalan todas las dependencias necesarias
   - Se optimiza el tamaño de la imagen

2. **Configuración de la Aplicación**:
   - Se copian los archivos necesarios
   - Se configuran las variables de entorno

3. **Optimización**:
   - Se eliminan archivos temporales
   - Se reduce el tamaño de la imagen

### 3. Publicación

La imagen construida se publica en GitHub Container Registry:

```yaml
- name: Build and push
  uses: docker/build-push-action@v4
  with:
    context: .
    push: true
    tags: |
      ghcr.io/salazarbryan13/gestor-citas:latest
      ghcr.io/salazarbryan13/gestor-citas:${{ github.sha }}
```

## Variables de Entorno

El proceso de build requiere varias variables de entorno para funcionar correctamente:

- `DATABASE_URL`: URL de conexión a la base de datos
- `SECRET_KEY`: Clave secreta para la aplicación
- `ENVIRONMENT`: Entorno de ejecución (development/production)

## Optimizaciones Implementadas

1. **Multi-stage Build**:
   - Reduce el tamaño final de la imagen
   - Mejora la seguridad al no incluir herramientas de desarrollo

2. **Caché de Capas**:
   - Acelera el proceso de construcción
   - Reduce el consumo de recursos

3. **Optimización de Dependencias**:
   - Instalación selectiva de paquetes
   - Eliminación de archivos temporales

## Verificación de la Construcción

Para verificar que la construcción fue exitosa:

1. **Inspección de la Imagen**:
   ```bash
   docker inspect ghcr.io/salazarbryan13/gestor-citas:latest
   ```

2. **Prueba Local**:
   ```bash
   docker run -d -p 8000:8000 ghcr.io/salazarbryan13/gestor-citas:latest
   ```

3. **Verificación de Logs**:
   ```bash
   docker logs gestor-citas
   ```

## Conclusiones

El proceso de build implementado proporciona una base sólida para el despliegue de la aplicación. Las optimizaciones realizadas aseguran que la imagen final sea eficiente y segura, mientras que la automatización mediante GitHub Actions garantiza un proceso de construcción consistente y confiable.

## Recomendaciones

1. **Monitoreo de Tamaño**:
   - Implementar alertas para el tamaño de la imagen
   - Revisar periódicamente las dependencias

2. **Seguridad**:
   - Escaneo de vulnerabilidades en la imagen
   - Actualización regular de la imagen base

3. **Optimización**:
   - Revisar y actualizar las dependencias
   - Implementar compresión de capas 