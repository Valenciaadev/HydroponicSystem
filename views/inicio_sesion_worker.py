from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QLabel, QHBoxLayout, QAction
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QSize
from controllers.auth_controller import login_user
# from main import switch_to_register
from views.homeapp_worker import HomeappWorker

class InicioSesionWidget(QWidget):
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

        layout.addLayout(form_layout)
        
        button_layout = QHBoxLayout()

        # Botones
        login_button = QPushButton(" Iniciar sesión")
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
        
        back_button = QPushButton(" Volver")
        back_button.setIcon(QIcon("assets/icons/btn-undo-white.svg"))
        back_button.setIconSize(QSize(24, 24))
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #555;
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
        
        # switch_button = QPushButton("¿No tienes una cuenta?, Regístrate")
        # switch_button.setStyleSheet("""
        #     QPushButton {
        #         background-color: transparent;
        #         color: #0078D7;
        #         font-size: 12px;
        #         border: none;
        #         text-decoration: underline;
        #     }
        #     QPushButton:hover {
        #         color: #005A9E;
        #     }
        #     QPushButton:pressed {
        #         color: #004080;
        #     }
        # """)
        # switch_button.clicked.connect(switch_to_register)

        # layout.addWidget(switch_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def login_action(self):
        email = self.email_input.text()
        password = self.password_input.text()
        
        if login_user(email, password):
            self.parent_app.mostrar_panel_worker()
    
    def back_to_selection(self):
        if self.parent_app:
            self.parent_app.switch_to_user_selection()