# Flask imports
from flask import (
    Flask,  # Instancia principal de la aplicación Flask
    render_template,  # Renderiza plantillas HTML
    request,  # Manejo de solicitudes HTTP
    session,  # Almacenamiento de datos de sesión
    redirect,  # Redirecciona a otras rutas
    url_for,  # Genera URLs para funciones de vista
    Response,  # Respuesta HTTP personalizada
    jsonify,  # Convierte objetos en respuestas JSON
)

# Configuración de la aplicación
import config

# MySQL para Flask
from flask_mysqldb import MySQL

# Manipulación de fechas y horas
from datetime import datetime

# Generación de PDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# Manipulación de flujos de bytes
from io import BytesIO


# Creación de una instancia de la aplicación Flask
app = Flask(__name__)

# Configuración de la aplicación
app.config[
    "SECRET_KEY"
] = config.HEX_SEC_KEY  # Configuración de la clave secreta para la sesión
app.config[
    "MYSQL_HOST"
] = config.MYSQL_HOST  # Configuración del host de la base de datos MySQL
app.config[
    "MYSQL_USER"
] = config.MYSQL_USER  # Configuración del usuario de la base de datos MySQL
app.config[
    "MYSQL_PASSWORD"
] = config.MYSQL_PASSWORD  # Configuración de la contraseña de la base de datos MySQL
app.config[
    "MYSQL_DB"
] = config.MYSQL_DB  # Configuración del nombre de la base de datos MySQL

# Inicialización de la extensión MySQL con la aplicación
mysql = MySQL(app)


# Definición de una ruta para la página principal
@app.route("/", methods=["GET"])
def home():
    # Renderiza la plantilla "index.html" al acceder a la ruta principal
    return render_template("index.html")


# Ruta para la autenticación de usuarios mediante el método POST
@app.route("/login", methods=["POST"])
def login():
    # Obtener el correo electrónico y la contraseña desde el formulario de la solicitud
    email = request.form["email"]
    password = request.form["password"]

    # Se Crea un cursor para interactuar con la base de datos MySQL
    cur = mysql.connection.cursor()

    # Ejecuta una consulta para seleccionar un usuario con el correo electrónico y la contraseña proporcionados
    cur.execute(
        "SELECT * FROM users WHERE email = %s AND password = %s", (email, password)
    )

    # Obtiene el primer resultado de la consulta
    user = cur.fetchone()

    # Cerrar el cursor después de la consulta
    cur.close()

    # Verificar si se encontró un usuario con las credenciales proporcionadas
    if user is not None:
        # Almacena la información del usuario en la sesión
        session["email"] = email
        session["name"] = user[1]
        session["surnames"] = user[2]
        session["role"] = user[5]

        # Redirige a la ruta "tasks" después de una autenticación exitosa
        return redirect(url_for("tasks"))
    else:
        # Renderiza la plantilla "index.html" con un mensaje de error si las credenciales no son correctas
        return render_template(
            "index.html", message="Las credenciales no son correctas"
        )


# Ruta para mostrar la información de todos los usuarios (solo accesible poara los administradores)
@app.route("/users", methods=["GET"])
def users():
    # Verificar si el usuario que accede es un administrador
    if session.get("role") != "admin":
        # Redirigir a la página principal si el usuario no es un administrador
        return redirect(url_for("home"))

    # Se Crea un cursor para interactuar con la base de datos MySQL
    cur = mysql.connection.cursor()

    # Ejecutar una consulta para seleccionar todos los usuarios en la base de datos
    cur.execute("SELECT * FROM users")

    # Obtiene todos los resultados de la consulta
    users = cur.fetchall()

    # Cerrar el cursor después de la consulta
    cur.close()

    # Se Crea una lista de diccionarios para almacenar la información de cada usuario
    user_list = []
    for user in users:
        user_dict = {
            "id": user[0],
            "name": user[1],
            "surnames": user[2],
            "email": user[3],
            "password": user[4],
            "role": user[5],
        }
        user_list.append(user_dict)

    # Renderizar la plantilla "users.html" con la lista de usuarios
    return render_template("users.html", users=user_list)


# Ruta para cambiar dinámicamente el color del contenedor mediante solicitudes POST
@app.route("/change-color", methods=["POST"])
def change_color():
    # Obtiene el estado actual del color del contenedor de la sesión, predeterminado a "light" si no está presente
    current_color = session.get("current_color", "light")

    # Cambia el color opuesto al estado actual
    if current_color == "light":
        session["current_color"] = "dark"
    else:
        session["current_color"] = "light"

    # Devuelve el nuevo estado del color como respuesta JSON
    return jsonify({"color": session["current_color"]})


# Ruta para mostrar las tareas asociadas al usuario actual
@app.route("/tasks", methods=["GET"])
def tasks():
    # Obtener el correo electrónico del usuario de la sesión
    email = session["email"]

    # Se Crea un cursor para interactuar con la base de datos MySQL
    cur = mysql.connection.cursor()

    # Se Ejecuta una consulta para seleccionar todas las tareas asociadas al usuario por su correo electrónico
    cur.execute("SELECT * FROM tasks WHERE email = %s", [email])

    # Obtener todas las tareas asociadas al usuariobb
    tasks = cur.fetchall()

    # Crear una lista de diccionarios para almacenar la información de cada tarea 
    insertObject = []
    columnNames = [column[0] for column in cur.description]

    # Convertir los resultados de la consulta a un diccionario
    for record in tasks:
        insertObject.append(dict(zip(columnNames, record)))

    # Cerrar el cursor después de la consulta
    cur.close()

    # Renderizar la plantilla "tasks.html" con la lista de tareas
    return render_template("tasks.html", tasks=insertObject)


# Ruta para mostrar las tareas asociadas al usuario actual
@app.route("/vistas", methods=["GET"])
def vistas():
    # Obtener el correo electrónico del usuario de la sesión
    email = session["email"]

    # Se Crea un cursor para interactuar con la base de datos MySQL
    cur = mysql.connection.cursor()

    # Se Ejecuta una consulta para seleccionar todas las tareas asociadas al usuario por su correo electrónico
    cur.execute("SELECT * FROM tasks WHERE email = %s", [email])

    # Obtener todas las tareas asociadas al usuario
    tasks = cur.fetchall()

    # Crear una lista de diccionarios para almacenar la información de cada tarea
    insertObject = []
    columnNames = [column[0] for column in cur.description]

    # Convertir los resultados de la consulta a un diccionario
    for record in tasks:
        insertObject.append(dict(zip(columnNames, record)))

    # Cerrar el cursor después de la consulta
    cur.close()

    # Renderizar la plantilla "vistas.html" con la lista de tareas
    return render_template("vistas.html", tasks=insertObject)


# Ruta para cerrar la sesión de usuario y redirigir a la página principal
@app.route("/logout")
def logout():
    # Limpiar todos los datos de la sesión
    session.clear()

    # Redirigir a la página principal
    return redirect(url_for("home"))


# Ruta para agregar una nueva tarea a la base de datos mediante solicitudes POST
@app.route("/new-task", methods=["POST"])
def newTask():
    # Obtener datos del formulario de la solicitud
    title = request.form["title"]
    description = request.form["description"]
    email = session["email"]

    # Obtener la fecha y hora actual
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Verificar que se proporcionaron título, descripción y correo electrónico
    if title and description and email:
        # Se Crea un cursor para interactuar con la base de datos MySQL
        cur = mysql.connection.cursor()

        # Se Define la consulta SQL para insertar una nueva tarea en la base de datos
        sql = "INSERT INTO tasks (email, title, description, date_task) VALUES (%s, %s, %s, %s)"
        data = (email, title, description, current_time)

        # Se Ejecuta la consulta SQL con los datos proporcionados
        cur.execute(sql, data)

        # Confirmar la transacción en la base de datos
        mysql.connection.commit()

    # Redirigir a la página de tareas después de agregar la nueva tarea
    return redirect(url_for("tasks"))


# Ruta para agregar un nuevo usuario a la base de datos mediante solicitudes POST
@app.route("/new-user", methods=["POST"])
def newUser():
    # Obtener datos del formulario de la solicitud
    name = request.form["name"]
    surnames = request.form["surnames"]
    email = request.form["email"]
    password = request.form["password"]

    # Obtener el rol desde el formulario, con "user" como valor predeterminado si no se proporciona
    role = request.form.get("role", "user")

    # Verificar si el usuario que está creando el nuevo usuario => es un administrador
    if session.get("role") == "admin":
        # El usuario que crea el nuevo usuario => es un administrador, asignar el rol correspondiente

        # Verificar que se proporcionaron nombre, apellidos, correo electrónico y contraseña
        if name and surnames and email and password:
            # Se Crea un cursor para interactuar con la base de datos MySQL
            cur = mysql.connection.cursor()

            # Se Define la consulta SQL para insertar un nuevo usuario en la base de datos
            sql = "INSERT INTO users (name, surnames, email, password, role) VALUES (%s, %s, %s, %s, %s)"
            data = (name, surnames, email, password, role)

            # Ejecutar la consulta SQL con los datos proporcionados
            cur.execute(sql, data)

            # Confirmar la transacción en la base de datos
            mysql.connection.commit()

        # Redirigir a la página de tareas después de agregar el nuevo usuario
        return redirect(url_for("tasks"))

    else:
        # El usuario que crea el nuevo usuario => no es un administrador, asignar el rol por defecto
        return redirect(url_for("tasks", message="No tienes permisos para esta acción"))


# Ruta para eliminar una tarea específica de la base de datos mediante solicitudes POST
@app.route("/delete_task", methods=["POST"])
def deleteTask():
    # Se Crea un cursor para interactuar con la base de datos MySQL
    cur = mysql.connection.cursor()

    # Se Obtiene el ID de la tarea a eliminar desde el formulario de la solicitud
    id = request.form["id"]

    # Se Define la consulta SQL para eliminar la tarea con el ID proporcionado
    sql = "DELETE FROM tasks WHERE id = %s"
    data = (id,)

    # Se Ejecuta la consulta SQL con los datos proporcionados
    cur.execute(sql, data)

    # Confirmar la transacción en la base de datos
    mysql.connection.commit()

    # Redirigir a la página de tareas después de eliminar la tarea
    return redirect(url_for("tasks"))


# Ruta para descargar un informe en formato PDF con la información de las tareas del usuario
@app.route("/download-report")
def download_report():
    # Se verifica de que el usuario haya iniciado sesión
    if "email" not in session:
        # Redirigir a la página principal si el usuario no ha iniciado sesión
        return redirect(url_for("home"))

    # Se Obtiene el correo electrónico del usuario de la sesión
    email = session["email"]

    # Se Crea un cursor para interactuar con la base de datos MySQL
    cur = mysql.connection.cursor()

    # Se Ejecuta una consulta para seleccionar todas las tareas asociadas al usuario por su correo electrónico
    cur.execute("SELECT * FROM tasks WHERE email = %s", [email])

    # Se Obtiene todas las tareas asociadas al usuario
    tasks = cur.fetchall()

    # Cerrar el cursor después de la consulta
    cur.close()

    # Se Crea un archivo PDF en memoria
    pdf_buffer = BytesIO()
    pdf = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    # Lista de elementos para el documento
    elements = []

    # Título del documento
    title = "Aplicación Web de Tareas"
    title_paragraph = Paragraph(f"<b>{title}</b>", getSampleStyleSheet()["Title"])
    elements.append(title_paragraph)
    elements.append(Spacer(1, 40))  # Espaciado después del título

    # Añadir una tabla para cada tarea
    for task in tasks:
        data = [
            [
                "ID   ",
                "Email    ",
                "Título   ",
                "Descripción                ",
                "Fecha de Tarea    ",
            ],
            [
                str(task[0]),
                task[1],
                task[2],
                Paragraph(task[3], getSampleStyleSheet()["BodyText"]),
                task[4],
            ],
        ]

        # Crear la tabla
        table = Table(data)

        # Aplicar estilos a la tabla
        style = TableStyle(
            [
                # Fila de encabezado: Fondo gris y texto blanco
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                # Alineación de todo el contenido al centro
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                # Estilo de fuente negrita para la fila de encabezado
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                # Espaciado en la parte inferior de la fila de encabezado
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                # Fila de datos: Fondo beige
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                # Líneas de la cuadrícula de la tabla
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                # Alineación vertical al medio en todas las celdas
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                # Líneas internas de la tabla con un grosor menor
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
                # Borde exterior de la tabla con un grosor
                ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                # Hacer que la descripción ocupe varias filas en la tercera columna
                ("SPAN", (3, 1), (3, 1)),
            ]
        )

        # Aplicar los estilos definidos a la tabla
        table.setStyle(style)

        # Añadir la tabla con los estilos aplicados a la lista de elementos
        elements.append(table)

        # Añadir un espacio adicional entre las tablas en la lista de elementos
        elements.append(Spacer(1, 12))

    # Compilar el documento con los elementos
    pdf.build(elements)

    # Posicionar el puntero de lectura del buffer al inicio
    pdf_buffer.seek(0)

    # Crear una respuesta con el archivo PDF adjunto
    response = Response(pdf_buffer.read(), content_type="application/pdf")

    # Establecer el encabezado Content-Disposition para indicar la descarga del archivo con un nombre específico
    response.headers["Content-Disposition"] = "attachment; filename=report.pdf"

    # Devolver la respuesta con el archivo PDF
    return response


# Verificar si el script se está ejecutando directamente como el programa principal
if __name__ == "__main__":
    # Iniciar la ejecución de la aplicación Flask en modo de depuración
    app.run(debug=True)
