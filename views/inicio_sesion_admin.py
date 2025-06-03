from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore
from controllers.auth_controller import login_user
from controllers.auth_controller import show_message
from views.homeapp_admin import HomeappAdmin
from models.database import connect_db
import mysql.connector
import bcrypt
import re

class InicioSesionAdministradorWidget(QWidget):
    def __init__(self, parent_app=None):
        super().__init__()
        self.parent_app = parent_app
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Título
        title_label = QLabel("Inicia sesión")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Candara", 20))
        title_label.setStyleSheet("color: white; padding-bottom: 20px; font: bold;")
        layout.addWidget(title_label)

        # Campos de entrada
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Ingresa tu correo electrónico")
        self.email_input.setFont(QFont("Candara", 10))
        self.email_input.setStyleSheet("font: bold; padding: 10px; border: 2px solid #ccc; border-radius: 5px; color: white;")
        self.email_input.returnPressed.connect(self.login_action)
        
        icon_action = QAction(QIcon("assets/icons/correo-white.svg"), "", self)
        self.email_input.addAction(icon_action, QLineEdit.LeadingPosition)
        form_layout.addRow("", self.email_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setFont(QFont("Candara", 10))
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("font: bold; padding: 10px; border: 2px solid #ccc; border-radius: 5px; color: white;")
        self.password_input.returnPressed.connect(self.login_action)
        
        password_icon_action = QAction(QIcon("assets/icons/password-white.svg"), "", self)
        self.password_input.addAction(password_icon_action, QLineEdit.LeadingPosition)
        form_layout.addRow("", self.password_input)
        
        self.cambiar_contraseña = QLabel("¿Olvidate tu contraseña?")
        self.cambiar_contraseña.setStyleSheet("font-size: 18px; color: #fff;")
        self.cambiar_contraseña.setAlignment(Qt.AlignCenter)
        self.cambiar_contraseña.setContentsMargins(10,10,10,10)
        self.cambiar_contraseña.mousePressEvent = lambda _: self.modal_cambiar_contrasena()
        form_layout.addRow(self.cambiar_contraseña)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        
        # Botones
        login_button = QPushButton("Iniciar sesión")
        login_button.setIcon(QIcon("assets/icons/btn-enter-white.svg"))
        login_button.setIconSize(QSize(24, 24))
        login_button.setStyleSheet("""
            QPushButton {
                background-color: blue;
                color: white;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                font: bold;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
            QPushButton:pressed {
                background-color: #004080;
            }
        """)
        login_button.clicked.connect(self.login_action)
        button_layout.addWidget(login_button)
        
        
        back_button = QPushButton("Volver")
        back_button.setIcon(QIcon("assets/icons/btn-undo-white.svg"))
        back_button.setIconSize(QSize(24, 24))
        back_button.setStyleSheet("""
            QPushButton {
                background-color: gray;
                color: white;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                font: bold;
            }
            QPushButton:hover {
                background-color: #444;
            }
        """)
        
        back_button.clicked.connect(self.back_to_selection)
        button_layout.addWidget(back_button)
        
        
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def create_gradient_input(self, placeholder_text=""):
        """Crea un input con el marco degradado como los actuadores"""
        outer_frame = QFrame()
        outer_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #60D4B8, stop:1 #1E2233);
                border-radius: 20px;
                padding: 2px;
            }
        """)
        outer_frame.setFixedHeight(45)

        inner_frame = QFrame()
        inner_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 18px;
            }
        """)

        layout = QHBoxLayout(inner_frame)
        layout.setContentsMargins(10, 0, 10, 0)

        input_field = QLineEdit()
        #input_field.setText(placeholder_text)
        input_field.setPlaceholderText(placeholder_text)
        input_field.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: white;
                font-size: 14px;
                padding: 5px;
            }
            QLineEdit::placeholder {
                color: #f1f1f1;  /* Color del texto */
                font-style: italic;  /* Cursiva */
            }
        """)
        layout.addWidget(input_field)

        outer_layout = QVBoxLayout(outer_frame)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(inner_frame)

        # Guardamos referencia al input
        outer_frame.input_field = input_field

        return outer_frame

    def modal_cambiar_contrasena(self):
    # Primer modal - Ingresar correo
        self.email_modal = QDialog(self)
        self.email_modal.setWindowTitle("Recuperar contraseña")
        self.email_modal.setFixedSize(400, 200)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(10,10,10,10)

        titulo = QLabel("Ingresa tu correo electrónico registrado:")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 16px; padding-bottom: 18px; font-weight: bold;")
        layout.addWidget(titulo)

        self.correo_input = self.create_gradient_input("Correo Electronico")
        layout.addWidget(self.correo_input)

        btn_siguiente = QPushButton("Siguiente")
        btn_siguiente.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        btn_siguiente.clicked.connect(self.verificar_correo)
        layout.addWidget(btn_siguiente)

        self.email_modal.setLayout(layout)
        self.email_modal.exec_()

    def verificar_correo(self):
        correo = self.correo_input.input_field.text()
        
        # Verificar si el correo existe en la base de datos
        conn = connect_db()
        if conn:
            try:
                cursor = conn.cursor()
                query = "SELECT id FROM usuarios WHERE email = %s"
                cursor.execute(query, (correo,))
                resultado = cursor.fetchone()
                
                if resultado:
                    self.user_id = resultado[0]  # Guardamos el ID del usuario
                    # CORRECCIÓN: Cerrar el primer modal antes de abrir el segundo
                    self.email_modal.close()  # Cierra el modal de email
                    self.mostrar_modal_nueva_contraseña()
                else:
                    QMessageBox.warning(self, "Error", "El correo electrónico no está registrado.")
                
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error", f"Error al verificar el correo: {err}")
            finally:
                conn.close()
        else:
            QMessageBox.critical(self, "Error", "No se pudo conectar a la base de datos.")

    def mostrar_modal_nueva_contraseña(self):
        # Segundo modal - Nueva contraseña
        self.password_modal = QDialog(self)
        self.password_modal.setWindowTitle("Nueva contraseña")
        self.password_modal.setFixedSize(400, 250)

        layout = QVBoxLayout()

        titulo = QLabel("Ingresa tu nueva contraseña:")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 16px; padding-bottom: 18px; font-weight: bold;")
        layout.addWidget(titulo)

        self.nueva_password_input = self.create_gradient_input("Nueva Contraseña")
        self.nueva_password_input.input_field.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.nueva_password_input)

        self.confirmar_password_input = self.create_gradient_input("Confirmar Contraseña")
        self.confirmar_password_input.input_field.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirmar_password_input)

        btn_cambiar = QPushButton("Cambiar contraseña")
        btn_cambiar.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        btn_cambiar.clicked.connect(self.cambiar_contrasena_db)
        layout.addWidget(btn_cambiar)

        self.password_modal.setLayout(layout)
        self.password_modal.exec_()
        
    def cambiar_contrasena_db(self):
        nueva_password = self.nueva_password_input.input_field.text().strip()
        confirmar_password = self.confirmar_password_input.input_field.text().strip()
        self.PASSWORD_MIN_LENGTH = 8

        if not nueva_password or not confirmar_password:
            QMessageBox.warning(self, "Error", "Ambos campos son obligatorios.")
            return

        if len(nueva_password) >= self.PASSWORD_MIN_LENGTH:
            QMessageBox.warning(self, "Error", 
                f"La contraseña debe tener al menos {self.PASSWORD_MIN_LENGTH} caracteres.")
            return

        if nueva_password != confirmar_password:
            QMessageBox.warning(self, "Error", "Las contraseñas no coinciden.")
            return

        try:
            salt = bcrypt.gensalt()
            password_encriptada = bcrypt.hashpw(nueva_password.encode('utf-8'), salt)
            password_encriptada_str = password_encriptada.decode('utf-8')

            conn = connect_db()
            if not conn:
                raise ConnectionError("No se pudo conectar a la base de datos")
                
            try:
                with conn.cursor() as cursor:
                    query = "UPDATE usuarios SET password = %s WHERE id = %s"
                    cursor.execute(query, (password_encriptada_str, self.user_id))
                    conn.commit()
                    
                    if cursor.rowcount > 0:
                        QMessageBox.information(self, "Éxito", "Contraseña cambiada correctamente.")
                        self.password_modal.close()
                    else:
                        QMessageBox.warning(self, "Error", "No se pudo cambiar la contraseña.")
            finally:
                if conn.is_connected():
                    conn.close()
                    
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error", f"Error de base de datos: {err}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error inesperado: {str(e)}")

    def login_action(self):
        email = self.email_input.text()
        password = self.password_input.text()

        user_data = login_user(email, password, parent=self)
        
        if user_data:
            if user_data["tipo_usuario"] == "administrador":
                show_message("Inicio de sesión exitoso", f"¡Bienvenid@, {user_data['nombre']}!", "success", self)
                self.parent_app.mostrar_panel_admin()
                # (nombre=user_data["nombre"])
            else:
                show_message("Acceso denegado", "Este usuario no tiene acceso a esta sección.", "warning", self)
        else:
            show_message("Inicio de sesión fallido", "Correo o contraseña incorrectos.", "warning", self)
        
    def back_to_selection(self):
        if self.parent_app:
            self.parent_app.switch_to_user_selection()