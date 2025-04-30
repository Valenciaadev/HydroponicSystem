from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QDialog, QTextBrowser, QDialog, QHBoxLayout
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QSize

# Controlador para manejar creación de dispositivos (debes crearlo tú)
#from controllers.device_controller import create_device

class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(30)
        self.setStyleSheet("background-color: #1E1B2E; color: white;")

        layout = QHBoxLayout()
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(5)

        self.title = QLabel("Sistema Hidropónico")
        self.title.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.title)

        self.minimize_button = QPushButton("")
        self.minimize_button.setIcon(QIcon("assets/icons/btn-minimize-white.svg"))
        self.minimize_button.setIconSize(QSize(24, 24))
        self.minimize_button.setFixedSize(30, 30)
        self.minimize_button.setStyleSheet("background-color: transparent; color: white;")
        self.minimize_button.clicked.connect(self.parent.showMinimized)
        self.minimize_button.setCursor(Qt.PointingHandCursor)
        self.minimize_button.setStyleSheet("QPushButton:hover { background-color: blue; }")
        layout.addWidget(self.minimize_button)

        
        self.close_button = QPushButton("")
        self.close_button.setIcon(QIcon("assets/icons/btn-close-white.svg"))
        self.close_button.setIconSize(QSize(24, 24))
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet("background-color: transparent; color: white;")
        self.close_button.clicked.connect(self.parent.close)
        self.close_button.setCursor(Qt.PointingHandCursor)
        self.close_button.setStyleSheet("QPushButton:hover { background-color: blue; }")
        layout.addWidget(self.close_button)
        
        self.setLayout(layout)
        self.drag_position = None

    def toggle_maximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.parent.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            self.parent.move(event.globalPos() - self.drag_position)
            event.accept()

class CreateDeviceWidget(QDialog):
    def __init__(self, ventana_login):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint)  # Elimina la barra de título predeterminada
        self.setFixedSize(300, 450)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Evita espacio en los bordes

        dialog = QDialog(self)

        self.title_bar = TitleBar(self)
        layout.addWidget(self.title_bar)

        title_label = QLabel("Registrar Dispositivo")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Candara", 20))
        title_label.setStyleSheet("color: white; padding: 10px; font-weight: bold;")
        layout.addWidget(title_label)

        form_layout = QFormLayout()
        form_layout.setContentsMargins(20, 0, 20, 0)

        # Nombre del dispositivo
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nombre del dispositivo")
        self.name_input.setFont(QFont("Candara", 10))
        self.name_input.setStyleSheet("font: bold; color: white; padding: 10px; border: 2px solid #ccc; border-radius: 5px;")
        form_layout.addRow("", self.name_input)

        # Modelo
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("Modelo")
        self.model_input.setFont(QFont("Candara", 10))
        self.model_input.setStyleSheet("font: bold; color: white; padding: 10px; border: 2px solid #ccc; border-radius: 5px;")
        form_layout.addRow("", self.model_input)

        # Número de serie
        self.serial_input = QLineEdit()
        self.serial_input.setPlaceholderText("Número de serie")
        self.serial_input.setFont(QFont("Candara", 10))
        self.serial_input.setStyleSheet("font: bold; color: white; padding: 10px; border: 2px solid #ccc; border-radius: 5px;")
        form_layout.addRow("", self.serial_input)

        # Descripción
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Descripción breve del dispositivo")
        self.desc_input.setFont(QFont("Candara", 10))
        self.desc_input.setStyleSheet("font: bold; color: white; padding: 10px; border: 2px solid #ccc; border-radius: 5px;")
        form_layout.addRow("", self.desc_input)

        layout.addLayout(form_layout)

        # Botón de registrar
        register_button = QPushButton("Aceptar")
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
        register_button.clicked.connect(self.register_device)

        switch_button = QPushButton("Volver")
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
        switch_button.clicked.connect(dialog.reject)
        layout.addWidget(switch_button)

        layout.addWidget(register_button)
        self.setLayout(layout)

    def register_device(self):
        name = self.name_input.text()
        model = self.model_input.text()
        serial = self.serial_input.text()
        description = self.desc_input.text()

        if not name or not model or not serial:
            QMessageBox.warning(self, "Campos obligatorios", "Por favor, completa todos los campos obligatorios.")
            return

        # success = create_device(name, model, serial, description)

        # if success:
            # QMessageBox.information(self, "Éxito", "Dispositivo registrado exitosamente.")
            # self.name_input.clear()
            # self.model_input.clear()
            # self.serial_input.clear()
            # self.desc_input.clear()

            # if self.switch_to_dashboard:
                # self.switch_to_dashboard()
        # else:
            # QMessageBox.critical(self, "Error", "Hubo un error al registrar el dispositivo.")
