from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from controllers.auth_controller import login_user

class InicioSesionAdministradorWidget(QWidget):
    def __init__(self):
        super().__init__()

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
        form_layout.addRow("", self.email_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setFont(QFont("Candara", 10))
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("font: bold; margin-bottom: 40px; padding: 10px; border: 2px solid #ccc; border-radius: 5px; color: white;")
        form_layout.addRow("", self.password_input)

        layout.addLayout(form_layout)

        # Botones
        login_button = QPushButton("Iniciar sesión")
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #0078D7;
                color: white;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
            QPushButton:pressed {
                background-color: #004080;
            }
        """)
        login_button.clicked.connect(self.login_action)

        layout.addWidget(login_button)

        self.setLayout(layout)

    def login_action(self):
        email = self.email_input.text()
        password = self.password_input.text()
        
        login_user(email, password)