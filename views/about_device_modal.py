from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QDialog, QTextBrowser, QDialog, QHBoxLayout, QSizePolicy
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QSize

class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(30)
        self.setStyleSheet("background-color: #1E1B2E; color: white;")

        layout = QHBoxLayout()
        layout.setContentsMargins(5, 0, 5, 0)

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

class AboutDeviceWidget(QDialog):
    def __init__(self, ventana_login):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(380, 480)

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 0, 5, 10)

        self.title_bar = TitleBar(self)
        layout.addWidget(self.title_bar)

        title_label = QLabel("Registrar Dispositivo")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Candara", 20))
        title_label.setStyleSheet("""
            color: white; 
            margin: 0px;
            font-weight: bold;
        """)
        layout.addWidget(title_label)

        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        # Crear campos de entrada con estilo
        self.name_input = self.create_input("Nombre del dispositivo")
        form_layout.addRow("", self.name_input)

        self.model_input = self.create_input("Tipo de dispositivo")
        form_layout.addRow("", self.model_input)

        self.serial_input = self.create_input("Consumo")
        form_layout.addRow("", self.serial_input)

        self.desc_input = self.create_input("Modo de operación")
        form_layout.addRow("", self.desc_input)

        self.state_input = self.create_input("Estado inicial")
        form_layout.addRow("", self.state_input)

        form_widget = QWidget()
        form_widget.setLayout(form_layout)
        form_widget.setContentsMargins(0, 0, 0, 0)
        form_widget.setStyleSheet("margin-top: 0px; padding-top: 0px; margin-bottom: 0px;")

        layout.addWidget(form_widget)

        # Botón Aceptar
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
        register_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Botón Volver
        back_button = QPushButton("Volver")
        back_button.setIcon(QIcon("assets/icons/btn-undo-white.svg"))
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
        back_button.clicked.connect(self.reject)
        back_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Layout horizontal para los botones
        button_layout = QHBoxLayout()
        button_layout.addStretch(10)
        button_layout.addWidget(register_button)
        button_layout.addWidget(back_button)

        # Añadir el layout horizontal al layout principal
        layout.addLayout(button_layout)

        # Establecer layout principal
        self.setLayout(layout)

    def create_input(self, placeholder):
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        input_field.setFont(QFont("Candara", 10))
        input_field.setStyleSheet("""
            font: bold;
            color: white;
            background-color: #1E1B2E; 
            padding: 10px;
            border: 2px solid #ccc;
            border-radius: 5px;
        """)
        input_field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        return input_field

    def register_device(self):
        name = self.name_input.text()
        model = self.model_input.text()
        serial = self.serial_input.text()
        description = self.desc_input.text()

        if not name or not model or not serial:
            QMessageBox.warning(self, "Campos obligatorios", "Por favor, completa todos los campos obligatorios.")
            return