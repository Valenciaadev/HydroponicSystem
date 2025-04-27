from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QCheckBox, QDialog, QTextBrowser
from PyQt5.QtGui import QFont, QCursor
from PyQt5.QtCore import Qt
from controllers.auth_controller import register_user, is_valid_email

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

        # Campos de entrada
        # Nombre
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nombre")
        self.username_input.setFont(QFont("Candara", 10))
        self.username_input.setStyleSheet("font: bold; color: white; padding: 10px; border: 2px solid #ccc; border-radius: 5px;")
        form_layout.addRow("", self.username_input)
        
        # Apellidos
        self.apellido_p_input = QLineEdit()
        self.apellido_p_input.setPlaceholderText("Apellido paterno")
        self.apellido_p_input.setFont(QFont("Candara", 10))
        self.apellido_p_input.setStyleSheet("font: bold; color: white; padding: 10px; border: 2px solid #ccc; border-radius: 5px;")
        form_layout.addRow("", self.apellido_p_input)
        
        self.apellido_m_input = QLineEdit()
        self.apellido_m_input.setPlaceholderText("Apellido materno")
        self.apellido_m_input.setFont(QFont("Candara", 10))
        self.apellido_m_input.setStyleSheet("font: bold; color: white; padding: 10px; border: 2px solid #ccc; border-radius: 5px;")
        form_layout.addRow("", self.apellido_m_input)
        
        # Correo electrónico
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Correo electrónico; [ej. example@hotmail.com]")
        self.email_input.setFont(QFont("Candara", 10))
        self.email_input.setStyleSheet("font: bold; color: white; padding: 10px; border: 2px solid #ccc; border-radius: 5px;")
        form_layout.addRow("", self.email_input)
        
        # Número de teléfono
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Número de teléfono; [ej. 12334514325]")
        self.phone_input.setFont(QFont("Candara", 10))
        self.phone_input.setStyleSheet("font: bold; color: white; padding: 10px; border: 2px solid #ccc; border-radius: 5px;")
        form_layout.addRow("", self.phone_input)
        
        # Contraseña
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setFont(QFont("Candara", 10))
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("font: bold; color: white; margin-bottom: 40px; padding: 10px; border: 2px solid #ccc; border-radius: 5px;")
        form_layout.addRow("", self.password_input)

        layout.addLayout(form_layout)
        
        # Checkbox de términos y condiciones
        terms_layout = QVBoxLayout()
        self.terms_checkbox = QCheckBox()
        self.terms_checkbox.setStyleSheet("color: white; font-size: 12px;")

        terms_label = QLabel('Acepto los <a href="#"><span style="color:#00AEEF; text-decoration: underline;">Términos y Condiciones</span></a>')
        terms_label.setStyleSheet("color: white; font-size: 12px;")
        terms_label.setCursor(QCursor(Qt.PointingHandCursor))
        terms_label.setOpenExternalLinks(False)  # Para que maneje el clic internamente
        terms_label.linkActivated.connect(self.show_terms)

        terms_layout.addWidget(self.terms_checkbox)
        terms_layout.addWidget(terms_label)
        layout.addLayout(terms_layout)

        # Botones
        register_button = QPushButton("Registrarme")
        register_button.setStyleSheet("""
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
        register_button.clicked.connect(self.register_action)

        switch_button = QPushButton("¿Tienes una cuenta?, Inicia sesión!")
        switch_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #0078D7;
                font-size: 12px;
                border: none;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #005A9E;
            }
            QPushButton:pressed {
                color: #004080;
            }
        """)
        switch_button.clicked.connect(switch_to_login)

        layout.addWidget(register_button)
        layout.addWidget(switch_button)

        self.setLayout(layout)
        
    def show_terms(self):
        """Abre una ventana emergente con los términos y condiciones."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Términos y Condiciones")
        dialog.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()
        text_browser = QTextBrowser()
        text_browser.setText("""
            <h3>Términos y Condiciones</h3>
            <p>Bienvenido a nuestra plataforma. Antes de continuar, por favor lee los siguientes términos:</p>
            <ul>
                <li>No compartas tu contraseña con terceros.</li>
                <li>Respetar a los demás usuarios en la comunidad.</li>
                <li>No utilizar información falsa en el registro.</li>
                <li>El uso indebido de la plataforma puede resultar en la suspensión de la cuenta.</li>
            </ul>
            <p>Al continuar, aceptas estos términos.</p>
        """)
        text_browser.setOpenExternalLinks(True)

        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(dialog.accept)

        layout.addWidget(text_browser)
        layout.addWidget(close_button)
        dialog.setLayout(layout)
        dialog.exec_()

    def register_action(self):
        nombre = self.username_input.text()
        apellido_paterno = self.apellido_p_input.text()
        apellido_materno = self.apellido_m_input.text()
        email = self.email_input.text()
        telefono = self.phone_input.text()
        password = self.password_input.text()
        acepta_terminos = self.terms_checkbox.isChecked()

        # Llamamos a la función de registro
        registro_exitoso = register_user(nombre, apellido_paterno, apellido_materno, email, telefono, password, acepta_terminos)

        # Si el registro es exitoso, limpiamos los campos y cambiamos a la pantalla de login
        if registro_exitoso:
            self.username_input.clear()
            self.apellido_p_input.clear()
            self.apellido_m_input.clear()
            self.email_input.clear()
            self.phone_input.clear()
            self.password_input.clear()
            self.terms_checkbox.setChecked(False)

            # Redirigir a la pantalla de inicio de sesión automáticamente
            self.switch_to_login()  # Llama a la función de cambio de pantalla