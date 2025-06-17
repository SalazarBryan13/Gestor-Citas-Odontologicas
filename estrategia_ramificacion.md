# Estrategia de Ramificación

## Introducción

Este documento describe la estrategia de ramificación utilizada en el proyecto "Gestor de Citas Odontológicas". La estrategia está diseñada para facilitar el desarrollo colaborativo, la integración continua y la gestión de versiones, asegurando que el código en producción sea estable y que las nuevas características y correcciones se integren de manera ordenada.

## Ramas Principales

### 1. main
   - **Propósito**: Contiene el código en producción, utilizado por odontólogos y pacientes.
   - **Origen**: Creada al inicio del proyecto y mantenida estable.
   - **Fusiones Permitidas**: Solo recibe fusiones de las ramas `release/*` y `hotfix/*`.


### 2. develop
   - **Propósito**: Integración de nuevas características antes del despliegue a producción.
   - **Origen**: Creada desde `main` al inicio del proyecto.
   - **Fusiones Permitidas**: Recibe fusiones de las ramas `feature/*`, `bugfix/*`, `release/*` y `hotfix/*`.
  

## Ramas de Desarrollo

### 3. feature/*
   - **Propósito**: Desarrollo de nuevas características o funcionalidades.
   - **Origen**: Creada desde `develop`.
   - **Fusiones Permitidas**: Se fusiona de vuelta a `develop` una vez completada.
  

### 4. bugfix/*
   - **Propósito**: Corrección de errores identificados en `develop`.
   - **Origen**: Creada desde `develop`.
   - **Fusiones Permitidas**: Se fusiona de vuelta a `develop` una vez corregido.


## Ramas de Emergencia y Lanzamiento

### 5. hotfix/*
   - **Propósito**: Correcciones urgentes que deben aplicarse en producción.
   - **Origen**: Creada desde `main`.
   - **Fusiones Permitidas**: Se fusiona tanto en `main` como en `develop` para asegurar que la corrección esté presente en ambas ramas.
  
### 6. release/*
   - **Propósito**: Preparación de versiones para producción, incluyendo pruebas finales y ajustes.
   - **Origen**: Creada desde `develop`.
   - **Fusiones Permitidas**: Se fusiona tanto en `main` como en `develop` para asegurar que la versión esté lista para producción.


## Flujo de Trabajo

1. **Desarrollo de Características**:
   - Crear una rama `feature/*` desde `develop`.
   - Desarrollar y probar la nueva característica.
   - Fusionar de vuelta a `develop`.

2. **Corrección de Errores**:
   - Crear una rama `bugfix/*` desde `develop`.
   - Corregir y probar el error.
   - Fusionar de vuelta a `develop`.

3. **Correcciones Urgentes**:
   - Crear una rama `hotfix/*` desde `main`.
   - Corregir y probar el problema urgente.
   - Fusionar tanto en `main` como en `develop`.

4. **Preparación de Lanzamiento**:
   - Crear una rama `release/*` desde `develop`.
   - Realizar pruebas finales y ajustes.
   - Fusionar tanto en `main` como en `develop`.
