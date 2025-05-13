from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QDialog, QHBoxLayout, QSizePolicy, QSpacerItem, QFrame, QComboBox
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QSize
from controllers.auth_controller import show_message

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
        self.minimize_button.setStyleSheet("background-color: transparent;")
        self.minimize_button.clicked.connect(self.parent.showMinimized)
        self.minimize_button.setCursor(Qt.PointingHandCursor)
        self.minimize_button.setStyleSheet("QPushButton:hover { background-color: blue; }")
        layout.addWidget(self.minimize_button)

        self.close_button = QPushButton("")
        self.close_button.setIcon(QIcon("assets/icons/btn-close-white.svg"))
        self.close_button.setIconSize(QSize(24, 24))
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet("background-color: transparent;")
        self.close_button.clicked.connect(self.parent.close)
        self.close_button.setCursor(Qt.PointingHandCursor)
        self.close_button.setStyleSheet("QPushButton:hover { background-color: blue; }")
        layout.addWidget(self.close_button)

        self.setLayout(layout)
        self.drag_position = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.parent.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            self.parent.move(event.globalPos() - self.drag_position)
            event.accept()

class CreateSensorWidget(QDialog):
    def __init__(self, ventana_login):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(400, 500)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 5, 0, 10)

        self.title_bar = TitleBar(self)
        layout.addWidget(self.title_bar)

        title_label = QLabel("Registrar Sensor")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Candara", 14))
        title_label.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(title_label)

        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # Espaciado entre cada input(px)
        form_layout.setVerticalSpacing(15)

        self.name_input = self.create_input("Nombre del sensor")
        form_layout.addRow("", self.name_input)

        self.model_input = self.create_input("Tipo de sensor")
        form_layout.addRow("", self.model_input)

        self.serial_input = self.create_input("Consumo")
        form_layout.addRow("", self.serial_input)

        self.desc_input = self.create_input("Modo de operación")
        form_layout.addRow("", self.desc_input)

        self.state_input = QComboBox()
        self.state_input.setFont(QFont("Candara", 10))
        self.state_input.addItem("Estado inicial")  # Placeholder
        self.state_input.addItem("Encendido")
        self.state_input.addItem("Apagado")
        self.state_input.setCurrentIndex(0)
        self.state_input.setStyleSheet("""
            QComboBox {
                font: bold;
                color: #E0E0E0;
                background-color: #1E1B2E;
                padding: 10px;
                border: 2px solid #30EACE;
                border-radius: 20px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #1E1B2E;
                color: white;
                selection-background-color: #30EACE;
            }
        """)
        self.state_input.currentIndexChanged.connect(self.disable_placeholder_option)
        form_layout.addRow("", self.state_input)

        form_widget = QWidget()
        form_widget.setLayout(form_layout)
        layout.addWidget(form_widget)

        # --- Botón Aceptar con estilo degradado ---
        self.register_button = QPushButton("Aceptar")
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: #1E2233;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border: none;
                padding: 6px 18px;
            }
            QPushButton:hover {
                background-color: #1A3033;
            }
        """)
        self.register_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.register_button.clicked.connect(self.register_sensor)

        register_outer_frame = QFrame()
        register_outer_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #60D4B8, stop:1 #1E2233);
                border-radius: 30px;
                padding: 2px;
            }
        """)
        outer_layout = QVBoxLayout(register_outer_frame)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(self.register_button)

        # --- Botón Volver ---
        back_button = QPushButton("Volver")
        back_button.setIcon(QIcon("assets/icons/btn-undo-white.svg"))
        back_button.setStyleSheet("""
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
        back_button.clicked.connect(self.reject)
        back_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # --- Botones alineados a la derecha como antes ---
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.setSpacing(10)
        button_layout.addWidget(register_outer_frame)
        button_layout.addWidget(back_button)
        button_layout.addSpacerItem(QSpacerItem(15, 20, QSizePolicy.Fixed, QSizePolicy.Minimum))  # Ajusta 40 según cuánto quieras mover


        # Espaciado entre el último input y los botones
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def disable_placeholder_option(self, index):
        if self.state_input.itemText(index) != "Estado inicial":
            # Buscar el índice del placeholder por si no es el 0
            placeholder_index = self.state_input.findText("Estado inicial")
            if placeholder_index != -1:
                self.state_input.removeItem(placeholder_index)
    
    def create_input(self, placeholder):
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        input_field.setFont(QFont("Candara", 10))
        input_field.setStyleSheet("""
            QLineEdit {
                font: bold;
                color: #E0E0E0;
                background-color: #1E1B2E; 
                padding: 10px;
                border: 2px solid #30EACE;
                border-radius: 20px;
            }
            QLineEdit::placeholder {
                color: #E0E0E0;
            }
        """)
        input_field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        return input_field

    def register_sensor(self):
        name = self.name_input.text()
        model = self.model_input.text()
        serial = self.serial_input.text()
        desc = self.desc_input.text()
        state = self.state_input.currentText()

        if not name or not model or not serial or not desc:
            show_message("Campos obligatorios", "Por favor, completa todos los campos.", "error", self)
            return
        
        if state == "Estado inicial":
            show_message("Estado inválido", "Selecciona un estado inicial válido.", "error", self)
            return