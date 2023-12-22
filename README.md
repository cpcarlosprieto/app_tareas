
# Aplicación de Tareas en Flask

Esta aplicación web desarrollada en Flask permite gestionar tareas, usuarios y generar informes en formato PDF.

## Requisitos previos

Asegúrate de tener instalado Python en tu sistema. Puedes instalar las dependencias necesarias ejecutando:


pip install flask flask-mysqldb reportlab


## Configuración

Antes de ejecutar la aplicación, asegúrate de configurar la base de datos en el archivo `config.py`:

```python
# config.py

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = ""
MYSQL_DB = "nombre_base_datos"
HEX_SEC_KEY = "d5fb8c4fa8bd46638dadc4e751e0d68d"
```

## Iniciar la aplicación

Ejecuta el archivo `app.py` para iniciar la aplicación:

```bash
python app.py
```

La aplicación estará disponible en [http://localhost:5000/]

## Credenciales de inicio de sesión

- **Usuario Administrador:**
  - Email: `cp534496@gmail.com`
  - Contraseña: `carlos1234`

- **Usuario Normal:**
  - Email: `carlos@gmail.com`
  - Contraseña: `carlos123`

## Funcionalidades

- **Inicio de Sesión:**
  - Ingresa con las credenciales de administrador o usuario normal.

- **Gestión de Tareas:**
  - Crea, elimina y visualiza tareas.

- **Gestión de Usuarios:**
  - Solo disponible para administradores.
  - Crea nuevos usuarios especificando nombre, apellidos, email, contraseña y rol.

- **Generar Informe en PDF:**
  - Descarga un informe en PDF con las tareas asociadas al usuario autenticado.
