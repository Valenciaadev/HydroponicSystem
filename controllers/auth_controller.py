import bcrypt
import re
import mysql.connector
from models.database import connect_db
from PyQt5.QtWidgets import QMessageBox, QPushButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

# Autentificación para contraseña encriptada
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def show_message(title, message, type="info"):
    msg = QMessageBox()
    
    # Definir íconos y colores según el tipo de mensaje
    if type == "error":
        color = "#F10D32"  # Rojo fuerte para errores
        icon = "🚨"  # Emoji para simular el ícono
    elif type == "warning":
        color = "#F10D32"
        icon = "⚠️"
    elif type == "success":
        color = "#08D9D6"
        icon = "✅"
    else:
        color = "#08D9D6"
        icon = "ℹ️"
    
    # msg.setIcon(QMessageBox.Information)
    # Configurar la ventana y mensaje
    msg.setWindowTitle(title)
    msg.setText(f"<div style='text-align: center;'>"
                f"<h1>{icon}</h1>"
                f"<h2 style='color: white;'>{title}</h2>"
                f"<p style='font-size: 14px; color: white; font: bold;'>{message}</p></div>")
    
    # Remover botones automáticos y agregar uno personalizado
    msg.setStandardButtons(QMessageBox.NoButton)
    btn = msg.addButton("Aceptar", QMessageBox.AcceptRole)
    
    # Estilizar la ventana y el botón
    msg.setStyleSheet(f"""
        QMessageBox {{
            background-color: #201c35;  /* Fondo oscuro */
            border-radius: 10px;
            color: white;
            font-family: Arial;
            font-size: 14px;
        }}
        QPushButton {{
            background-color: {color}; /* Botón con color dinámico */
            color: white;
            border-radius: 10px;
            padding: 10px;
            font-weight: bold;
            min-width: 120px;
            text-align: center;
        }}
        QPushButton:hover {{
            background-color: #E43F5A; /* Color más fuerte al pasar el mouse */
        }}
    """)
    
    # Personalizar los botones
    # btn = msg.addButton("Aceptar", QMessageBox.AcceptRole)
    # btn.setStyleSheet("""
    #     QPushButton {
    #         background-color: #FF2E63;
    #         color: white;
    #         border-radius: 10px;
    #         padding: 10px;
    #         font-size: 14px;
    #         min-width: 100px;
    #     }
    #     QPushButton:hover {
    #         background-color: #E43F5A;
    #     }
    # """)
    
    msg.exec_()
    

# Validación del correo electrónico, que contenga @ y .com
def is_valid_email(email):
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.(com|mx)$", email))

def is_valid_phone(telefono):
    return telefono.isdigit() and len(telefono) == 10


# Función para registrar un nuevo usuario
def register_user(nombre, apellido_paterno, apellido_materno, email, telefono, password, acepta_terminos):
    if not all([nombre, apellido_paterno, apellido_materno, email, telefono, password]):
        show_message("Campos vacíos", "Por favor ingresa todos los campos.", "warning")
        return

    # Validar formato del correo electrónico
    if not is_valid_email(email):
        show_message("Correo inválido", "Por favor ingresa un correo electrónico válido.", "error")
        return
    
    # Validar número de teléfono
    if not is_valid_phone(telefono):
        show_message("Teléfono inválido", "El número de teléfono debe tener al menos 10 digitos.", "error")
        return False
    
    if not acepta_terminos:
        # QMessageBox.warning(None, "Términos y Condiciones", "Debes aceptar los términos y condiciones para registrarte.")
        show_message("Términos y Condiciones", "Debes aceptar los términos y condiciones para registrarte.", "error")
        return False
    
    conn = connect_db()
    if conn is None:
        show_message("Error", "No se pudo conectar a la base de datos.", "error")
        return False
    
    c = conn.cursor()
    c.execute("SELECT email FROM usuarios WHERE email=%s", (email,))
    
    if c.fetchone():
        show_message("Usuario ya existe", "El correo electrónico ya está registrado.", "warning")
        c.close()
        conn.close()
        return False
    
    # Cifrar la contraseña antes de almacenarla
    hashed_password = hash_password(password)

    try:
        c.execute("""
            INSERT INTO usuarios (nombre, apellido_paterno, apellido_materno, email, telefono, password) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nombre, apellido_paterno, apellido_materno, email, telefono, hashed_password))
        conn.commit()
        show_message("Registro exitoso", "¡Usuario registrado con éxito!", "success")
        return True
        
    except mysql.connector.IntegrityError as e:
        show_message("Error", "No se pudo registrar el usuario.", "error")
        print(f"Error SQL: {e}")
        return False
    
    finally:
        c.close()
        conn.close()

# Función para iniciar sesión
def login_user(email, password):
    """Inicia sesión validando correo y contraseña en la base de datos."""
    
    if not email or not password:
        show_message("Campos vacíos", "Por favor ingresa todos los campos.", "warning")
        return False

    conn = connect_db()
    if conn is None:
        show_message("Error", "No se pudo conectar a la base de datos.", "error")
        return False
    
    c = conn.cursor()

    c.execute("SELECT nombre, password FROM usuarios WHERE email=%s", (email,))
    user = c.fetchone()
    conn.close()

    if user and check_password(password, user[1]):
        show_message("Inicio de sesión exitoso", f"¡Bienvenido, {user[0]}!", "success")
        return True
    else:
        show_message("Inicio de sesión fallido", "Correo o contraseña incorrectos.", "warning")
        return False