# Estrategia de Ramificación

## Introducción

Este documento describe la estrategia de ramificación utilizada en el proyecto "Gestor de Citas Odontológicas". La estrategia está diseñada para facilitar el desarrollo colaborativo, la integración continua y la gestión de versiones, asegurando que el código en producción sea estable y que las nuevas características y correcciones se integren de manera ordenada.

## Ramas Principales

### 1. main
   - **Propósito**: Contiene el código en producción, utilizado por odontólogos y pacientes.
   - **Origen**: Creada al inicio del proyecto y mantenida estable.
   - **Fusiones Permitidas**: Solo recibe fusiones de las ramas `release/*` y `hotfix/*`.
   - **Ejemplo**: La versión actual en producción está en esta rama.

### 2. develop
   - **Propósito**: Integración de nuevas características antes del despliegue a producción.
   - **Origen**: Creada desde `main` al inicio del proyecto.
   - **Fusiones Permitidas**: Recibe fusiones de las ramas `feature/*`, `bugfix/*`, `release/*` y `hotfix/*`.
   - **Ejemplo**: Todas las nuevas características y correcciones se integran primero en esta rama.

## Ramas de Desarrollo

### 3. feature/*
   - **Propósito**: Desarrollo de nuevas características o funcionalidades.
   - **Origen**: Creada desde `develop`.
   - **Fusiones Permitidas**: Se fusiona de vuelta a `develop` una vez completada.
   - **Ejemplos**:
     - `feature/email-notifications`: Implementación de notificaciones por correo electrónico.
     - `feature/patient-registration`: Desarrollo del sistema de registro de pacientes.

### 4. bugfix/*
   - **Propósito**: Corrección de errores identificados en `develop`.
   - **Origen**: Creada desde `develop`.
   - **Fusiones Permitidas**: Se fusiona de vuelta a `develop` una vez corregido.
   - **Ejemplo**: `bugfix/duplicate-appointments`: Corrección para evitar citas duplicadas en el sistema.

## Ramas de Emergencia y Lanzamiento

### 5. hotfix/*
   - **Propósito**: Correcciones urgentes que deben aplicarse en producción.
   - **Origen**: Creada desde `main`.
   - **Fusiones Permitidas**: Se fusiona tanto en `main` como en `develop` para asegurar que la corrección esté presente en ambas ramas.
   - **Ejemplo**: `hotfix/dentist-login`: Corrección urgente en el sistema de inicio de sesión para odontólogos.

### 6. release/*
   - **Propósito**: Preparación de versiones para producción, incluyendo pruebas finales y ajustes.
   - **Origen**: Creada desde `develop`.
   - **Fusiones Permitidas**: Se fusiona tanto en `main` como en `develop` para asegurar que la versión esté lista para producción.
   - **Ejemplos**:
     - `release/v1.0.0`: Primera versión estable del sistema.
     - `release/v1.1.0`: Nueva versión con mejoras y correcciones.

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

## Mejores Prácticas

- **Nombres de Ramas**: Usar nombres descriptivos y seguir la convención establecida (ej., `feature/nombre-caracteristica`).
- **Commits**: Realizar commits pequeños y descriptivos, explicando claramente los cambios realizados.
- **Pull Requests**: Usar pull requests para revisar y discutir cambios antes de fusionar.
- **Pruebas**: Asegurar que todas las ramas pasen las pruebas antes de fusionar.
- **Documentación**: Mantener la documentación del proyecto actualizada, incluyendo este documento de estrategia de ramificación.

## Conclusión

Esta estrategia de ramificación permite un desarrollo ordenado y colaborativo, facilitando la integración de nuevas características y correcciones de errores mientras se mantiene la estabilidad del código en producción. Es importante seguir esta estrategia para asegurar la calidad y consistencia del proyecto. 