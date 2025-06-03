import bcrypt
import re
import mysql.connector
from models.database import connect_db
from PyQt5.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from views.seleccion_usuario import TitleBar


# Autentificación para contraseña encriptada
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def show_message(title, message, type="info", parent=None):
    dialog = QDialog(parent)
    dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
    dialog.setFixedSize(330, 220)
    dialog.setStyleSheet("""
        QDialog {
            background-color: #1E1B2E;
            border: 2px solid black;
            border-radius: 10px;
        }
    """)
        

    main_layout = QVBoxLayout()
    main_layout.setContentsMargins(10, 5, 10, 15)

    # Barra de título personalizada
    title_bar = TitleBar(dialog)
    main_layout.addWidget(title_bar)

    # Definir íconos y colores según el tipo de mensaje
    if type == "error":
        color = "#F10D32"  # Rojo fuerte para errores
    elif type == "warning":
        color = "#F10D32"
    elif type == "success":
        color = "#08D9D6"
    else:
        color = "#F10D32"

    content_layout = QVBoxLayout()

    label = QLabel(f"<div style='text-align: center;'>"
                    f"<h2 style='color: white;'>{title}</h2>"
                    f"<p style='font-size: 14px; color: white; font: bold;'>{message}</p></div>")
    label.setAlignment(Qt.AlignCenter)
    content_layout.addWidget(label)

    accept_button = QPushButton("Aceptar")
    accept_button.setStyleSheet(f"""
        QPushButton {{
            background-color: {color};
            color: white;
            border-radius: 10px;
            padding: 10px;
            font-weight: bold;
            min-width: 120px;
            text-align: center;
        }}
        QPushButton:hover {{
            background-color: #E43F5A;
        }}
    """)
    accept_button.clicked.connect(dialog.accept)
    content_layout.addWidget(accept_button, alignment=Qt.AlignCenter)

    main_layout.addLayout(content_layout)
    dialog.setLayout(main_layout)
    dialog.exec_()

# Validación del correo electrónico, que contenga @ y .com
def is_valid_email(email):
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.(com|mx)$", email))

def is_valid_phone(telefono):
    return telefono.isdigit() and len(telefono) == 10

# Función para registrar un nuevo usuario
def register_user(nombre, apellido_paterno, apellido_materno, email, telefono, password, acepta_terminos, parent=None):
    if not all([nombre, apellido_paterno, apellido_materno, email, telefono, password]):
        show_message("Campos vacíos", "Por favor ingresa todos los campos.", "warning", parent)
        return

    # Validar formato del correo electrónico
    if not is_valid_email(email):
        show_message("Correo inválido", "Por favor ingresa un correo electrónico válido.", "error", parent)
        return
    
    # Validar número de teléfono
    if not is_valid_phone(telefono):
        show_message("Teléfono inválido", "El número de teléfono debe tener al menos 10 digitos.", "error", parent)
        return False
    
    if not acepta_terminos:
        show_message("Términos y Condiciones", "Debes aceptar los términos y condiciones para registrarte.", "error", parent)
        return False
    
    conn = connect_db()
    if conn is None:
        show_message("Error", "No se pudo conectar a la base de datos.", "error", parent)
        return False
    
    c = conn.cursor()
    c.execute("SELECT email FROM usuarios WHERE email=%s", (email,))
    
    if c.fetchone():
        show_message("Usuari@ ya existe", "El correo electrónico ya está registrado.", "warning", parent)
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
        show_message("Registro exitoso", "¡Usuari@ registrado con éxito!", "success", parent)
        return True
        
    except mysql.connector.IntegrityError as e:
        show_message("Error", "No se pudo registrar el usuari@.", "error", parent)
        print(f"Error SQL: {e}")
        return False
    
    finally:
        c.close()
        conn.close()

# Función para iniciar sesión
def login_user(email, password, parent=None):
    """Inicia sesión validando correo y contraseña en la base de datos, y retorna info del usuario si es válida."""

    if not email or not password:
        show_message("Campos vacíos", "Por favor ingresa todos los campos.", "warning", parent)
        return None

    conn = connect_db()
    if conn is None:
        show_message("Error", "No se pudo conectar a la base de datos.", "error", parent)
        return None

    c = conn.cursor()
    c.execute("SELECT nombre, password, tipo_usuario FROM usuarios WHERE email=%s", (email,))
    user = c.fetchone()
    conn.close()

    if user and check_password(password, user[1]):
        # show_message("Inicio de sesión exitoso", f"¡Bienvenid@, {user[0]}!", "success", parent)
        return {"nombre": user[0], "tipo_usuario": user[2]}
    else:
        # show_message("Inicio de sesión fallido", "Correo o contraseña incorrectos.", "warning", parent)
        return None