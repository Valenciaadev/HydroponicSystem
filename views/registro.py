from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import bcrypt
from controllers.auth_controller import is_valid_email, is_valid_phone, show_message
from models.database import connect_db

class RegistroWidget(QWidget):
    def __init__(self, switch_to_login):
        super().__init__()

        self.switch_to_login = switch_to_login

        widget = QWidget()
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Título
        title_label = QLabel("Regístrate")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Candara", 20))
        title_label.setStyleSheet("color: white; padding-bottom: 20px; font: bold;")
        layout.addWidget(title_label)

        form_layout = QFormLayout()

        self.username = self.create_labeled_input("Nombre", "Ej. Juan")
        form_layout.addRow("", self.username)

        self.apellido_p = self.create_labeled_input("Apellido Paterno", "Ej. Pérez")
        form_layout.addRow("", self.apellido_p)

        self.apellido_m = self.create_labeled_input("Apellido Materno", "Ej. Gómez")
        form_layout.addRow("", self.apellido_m)

        # Selector de rol
        self.rol_combo = QComboBox()
        self.rol_combo.addItem("Selecciona el rol")
        self.rol_combo.addItem("Administrador")
        self.rol_combo.addItem("Trabajador")
        self.rol_combo.setFont(QFont("Candara", 10))
        self.rol_combo.setStyleSheet("""
            QComboBox {
                background-color: #1E1B2E;
                color: white;
                padding: 10px;
                border: 2px solid #30EACE;
                border-radius: 20px;
                font: bold;
            }
            QComboBox QAbstractItemView {
                background-color: #1E1B2E;
                color: white;
                selection-background-color: #30EACE;
            }
        """)

        def remove_default_role():
            if self.rol_combo.itemText(0) == "Selecciona el rol":
                self.rol_combo.removeItem(0)

        self.rol_combo.view().pressed.connect(remove_default_role)

        rol_container = QWidget()
        rol_layout = QVBoxLayout(rol_container)
        rol_layout.setContentsMargins(0, 0, 0, 0)
        rol_layout.setSpacing(2)

        rol_label = QLabel("Rol")
        rol_label.setFont(QFont("Candara", 12))
        rol_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 15px;
                font-weight: bold;
                margin-left: 12px;
                margin-bottom: 2px;
            }
        """)
        rol_layout.addWidget(rol_label)
        rol_layout.addWidget(self.rol_combo)

        form_layout.addRow("", rol_container)

        self.email = self.create_labeled_input("Correo electrónico", "Ej. correo@dominio.com")
        form_layout.addRow("", self.email)

        self.phone = self.create_labeled_input("Teléfono", "Ej. 1234567890")
        # self.phone.input_field.setValidator(QRegExpValidator(QRegExp("\\d{0,10}")))
        form_layout.addRow("", self.phone)

        self.password = self.create_labeled_input("Contraseña")
        self.password.input_field.setEchoMode(QLineEdit.Password)
        form_layout.addRow("", self.password)

        layout.addLayout(form_layout)
        layout.addSpacing(15)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        cancel_button = QPushButton("Cancelar")
        cancel_button.setIcon(QIcon("assets/icons/btn-undo-white.svg"))
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: 2px solid #444;
                border-radius: 30px;
                padding: 6px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #444;
            }
        """)
        cancel_button.clicked.connect(self.switch_to_login)
        cancel_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        accept_button = QPushButton("Aceptar")
        accept_button.setIcon(QIcon("assets/icons/btn-save-white.svg"))
        accept_button.setStyleSheet("""
            QPushButton {
                background-color: #30EACE;
                color: black;
                border: 2px solid #30EACE;
                border-radius: 30px;
                padding: 6px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #25C9B0;
            }
        """)
        accept_button.clicked.connect(self.register_action)
        accept_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(accept_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def create_labeled_input(self, label_text, placeholder=""):
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(2)

        label = QLabel(label_text)
        label.setFont(QFont("Candara", 12))
        label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 15px;
                font-weight: bold;
                margin-left: 12px;
                margin-bottom: 2px;
            }
        """)
        container_layout.addWidget(label)

        input_field = QLineEdit()
        input_field.setFont(QFont("Candara", 10))
        input_field.setPlaceholderText(placeholder)
        input_field.setStyleSheet("""
            QLineEdit {
                font: bold;
                color: white;
                background-color: #1E1B2E;
                padding: 10px;
                border: 2px solid #30EACE;
                border-radius: 20px;
            }
        """)
        container_layout.addWidget(input_field)
        container.input_field = input_field
        return container

    def register_action(self):
        nombre = self.username.input_field.text().strip()
        apellido_p = self.apellido_p.input_field.text().strip()
        apellido_m = self.apellido_m.input_field.text().strip()
        email = self.email.input_field.text().strip()
        telefono = self.phone.input_field.text().strip()
        password = self.password.input_field.text().strip()
        rol = self.rol_combo.currentText().lower()

        if rol == "selecciona el rol":
            show_message("Error", "Debes seleccionar un rol válido.", "error", self)
            return

        if not is_valid_email(email):
            show_message("Error", "Correo electrónico inválido.", "error", self)
            return

        if any(char.isdigit() for char in nombre):
            show_message("Error", "El nombre no puede contener números.", "error", self)
            return

        if any(char.isdigit() for char in apellido_p):
            show_message("Error", "El apellido no puede contener números.", "error", self)
            return

        if any(char.isdigit() for char in apellido_m):
            show_message("Error", "El apellido no puede contener números.", "error", self)
            return

        if not is_valid_phone(telefono):
            show_message("Error", "El número de teléfono no es válido", "error", self)
            return

        if not password:
            show_message("Error", "Debes ingresar una contraseña.", "error", self)
            return

        try:
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

                cursor.execute("""
                    INSERT INTO usuarios (nombre, apellido_paterno, apellido_materno, email, clabe, password, telefono, tipo_usuario)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (nombre, apellido_p, apellido_m, email, "789101", hashed_password, telefono, rol))
                conn.commit()
                user_id = cursor.lastrowid

                if rol == "trabajador":
                    cursor.execute("INSERT INTO trabajadores (id_usuario) VALUES (%s)", (user_id,))
                else:
                    cursor.execute("INSERT INTO administradores (id_usuario) VALUES (%s)", (user_id,))
                conn.commit()

                show_message("Éxito", "Usuario registrado correctamente.", "success", self)
                self.switch_to_login()

        except Exception as e:
            show_message("Error", f"Fallo al registrar usuario: {e}", "error", self)

        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals() and conn.is_connected():
                conn.close()
