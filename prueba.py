import sys
import bcrypt
import mysql.connector
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QFormLayout, QDialog, QStackedWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QMessageBox

def connect_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="Alexis",
            password="Maria12345",
            database="hydrophonic_sys",
            port=3306
        )
        print("✅ Conexión exitosa a la base de datos")
        return conn
    
    except mysql.connector.Error as err:
        print(f"❌ Error al conectar a la base de datos: {err}")
        return None

# Cifrar contraseña
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed

# Verificar contraseña
def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

# Función para registrar un nuevo usuario
def register_user(nombre, apellido_paterno, apellido_materno, email, telefono, password):
    if not all([nombre, apellido_paterno, apellido_materno, email, telefono, password]):
        show_message("Campos vacíos", "Por favor ingresa todos los campos.")
        return

    conn = connect_db()
    if conn is None:
        show_message("Error", "No se pudo conectar a la base de datos.")
        return
    
    c = conn.cursor()

    c.execute("SELECT * FROM usuarios WHERE email=%s", (email,))
    if c.fetchone():
        show_message("Usuario ya existe", "El correo electrónico ya está registrado.")
        conn.close()
        return
    
    # Cifrar la contraseña antes de almacenarla
    hashed_password = hash_password(password)

    try:
        c.execute("""
            INSERT INTO usuarios (nombre, apellido_paterno, apellido_materno, email, telefono, password) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nombre, apellido_paterno, apellido_materno, email, telefono, hashed_password))
        conn.commit()
        show_message("Registro exitoso", "¡Usuario registrado con éxito!")
    except mysql.connector.IntegrityError as e:
        show_message("Error", "No se pudo registrar el usuario.")
        print(f"❌ Error SQL: {e}")
    finally:
        conn.close()

# Función para iniciar sesión
def login_user(email, password):
    if email == "" or password == "":
        show_message("Campos vacíos", "Por favor ingresa todos los campos.")
        return

    conn = connect_db()
    if conn is None:
        show_message("Error", "No se pudo conectar a la base de datos.")
        return
    
    c = conn.cursor()

    # c.execute("SELECT * FROM usuarios WHERE email=%s AND password=%s", (email, password))
    c.execute("SELECT nombre, password FROM usuarios WHERE email=%s", (email,))
    user = c.fetchone()
    conn.close()

    if user and check_password(password, user[1]):
        show_message("Inicio de sesión exitoso", f"¡Bienvenido, {user[0]}!")
    else:
        show_message("Inicio de sesión fallido", "Nombre de usuario o contraseña incorrectos.")

# Mostrar mensajes
def show_message(title, message):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.exec_()

class LoginRegisterApp(QDialog):
    def __init__(self):
        super().__init__()

        #Creación de la ventana
        self.setWindowTitle("Sistema Hidropónico")
        self.setGeometry(800, 340, 500, 500)
        self.setStyleSheet("background-color: #f2f2f2;")
        self.setWindowFlags(Qt.Window)
        
        #Creación de la ventana de registro
        self.stack = QStackedWidget()
        self.register_widget = self.create_register_ui()
        self.login_widget = self.create_login_ui()
        self.stack.addWidget(self.register_widget)
        self.stack.addWidget(self.login_widget)
        
        #Layouts
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stack)
        self.setLayout(main_layout)
        
        # self.init_ui()
        
    def create_register_ui(self):
        widget = QWidget()
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        #Título
        title_label = QLabel("Regístrate")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 20))
        title_label.setStyleSheet("color: #4CAF50; padding-bottom: 20px;")
        layout.addWidget(title_label)
        
        #Campos de entrada
        #Nombre
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Ingresa tu nombre")
        self.username_input.setStyleSheet("font-size: 14px; padding: 10px; border: 2px solid #ccc; border-radius: 5px;")
        form_layout.addRow("Nombre:", self.username_input)
        
        #Apellidos
        self.apellido_p_input = QLineEdit()
        self.apellido_p_input.setPlaceholderText("Ingresa tu apellido paterno")
        self.apellido_p_input.setStyleSheet("font-size: 14px; padding: 10px; border: 2px solid #ccc; border-radius: 5px;")
        form_layout.addRow("Apellido paterno:", self.apellido_p_input)
        
        self.apellido_m_input = QLineEdit()
        self.apellido_m_input.setPlaceholderText("Ingresa tu apellido materno")
        self.apellido_m_input.setStyleSheet("font-size: 14px; padding: 10px; border: 2px solid #ccc; border-radius: 5px;")
        form_layout.addRow("Apellido materno:", self.apellido_m_input)
        
        #Correo
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Ingresa tu correo electrónico")
        self.email_input.setStyleSheet("font-size: 14px; padding: 10px; border: 2px solid #ccc; border-radius: 5px;")
        form_layout.addRow("Correo electrónico:", self.email_input)
        
        #Número telefónico
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Digite su número de teléfono")
        self.phone_input.setStyleSheet("font-size: 14px; padding: 10px; border: 2px solid #ccc; border-radius: 5px;")
        form_layout.addRow("Número de teléfono:", self.phone_input)
        
        #Contraseña
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("font-size: 14px; margin-bottom: 40px; padding: 10px; border: 2px solid #ccc; border-radius: 5px;")
        form_layout.addRow("Contraseña:", self.password_input)
        
        register_button = QPushButton("Registrar")
        register_button.clicked.connect(self.register_action)
        switch_button = QPushButton("Ir a Login")
        switch_button.clicked.connect(lambda: self.stack.setCurrentWidget(self.login_widget))
        layout.addLayout(form_layout)
        layout.addWidget(register_button)
        layout.addWidget(switch_button)
        widget.setLayout(layout)
        return widget
    
    def create_login_ui(self):
        widget = QWidget()
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        self.email_login_input = QLineEdit()
        
        
        title_label = QLabel("Inicia sesión")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 20))
        title_label.setStyleSheet("color: #4CAF50; padding-bottom: 20px;")
        layout.addWidget(title_label)
        
        #Correo
        self.email_login_input = QLineEdit()
        self.email_login_input.setPlaceholderText("Ingresa tu correo electrónico")
        self.email_login_input.setStyleSheet("font-size: 14px; padding: 10px; border: 2px solid #ccc; border-radius: 5px;")
        form_layout.addRow("Correo electrónico:", self.email_login_input)
        
        self.password_login_input = QLineEdit()
        self.password_login_input.setPlaceholderText("Contraseña")
        self.password_login_input.setEchoMode(QLineEdit.Password)
        self.password_login_input.setStyleSheet("font-size: 14px; margin-bottom: 40px; padding: 10px; border: 2px solid #ccc; border-radius: 5px;")
        form_layout.addRow("Contraseña:", self.password_login_input)
        
        login_button = QPushButton("Login")
        login_button.clicked.connect(self.login_action)
        switch_button = QPushButton("Ir a Registro")
        switch_button.clicked.connect(lambda: self.stack.setCurrentWidget(self.register_widget))
        layout.addLayout(form_layout)
        layout.addWidget(login_button)
        layout.addWidget(switch_button)
        widget.setLayout(layout)
        return widget

    def login_action(self):
        email = self.email_login_input.text()
        password = self.password_login_input.text()
        
        login_user(email, password)

    def register_action(self):
        nombre = self.username_input.text()
        apellido_paterno = self.apellido_p_input.text()
        apellido_materno = self.apellido_m_input.text()
        email = self.email_input.text()
        telefono = self.phone_input.text()
        password = self.password_input.text()
        register_user(nombre, apellido_paterno, apellido_materno, email, telefono, password)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginRegisterApp()
    window.show()
    sys.exit(app.exec_())