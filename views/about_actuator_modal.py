from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from models.database import connect_db


class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(30)
        self.setStyleSheet("background-color: #1E1B2E; color: white;")

        layout = QHBoxLayout()
        layout.setContentsMargins(5, 0, 5, 0)

        self.title = QLabel("Sistema Hidrop\u00f3nico")
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


class AboutActuatorWidget(QDialog):
    def __init__(self, ventana_login, actuator_id=None):
        super().__init__()
        self.actuator_id = actuator_id
        self.ventana_login = ventana_login
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(400, 550)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 5, 0, 10)

        self.title_bar = TitleBar(self)
        layout.addWidget(self.title_bar)

        title_label = QLabel("Características del actuador")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Candara", 14))
        title_label.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(title_label)

        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_layout.setVerticalSpacing(15)

        self.name_input = self.create_disabled_input("Nombre del actuador")
        form_layout.addRow("", self.name_input)

        self.tipo_input = self.create_disabled_input("Tipo")
        form_layout.addRow("", self.tipo_input)

        self.bus_input = self.create_disabled_input("Bus")
        form_layout.addRow("", self.bus_input)

        self.address_input = self.create_disabled_input("Address")
        form_layout.addRow("", self.address_input)

        self.modo_input = self.create_disabled_input("Modo de activación")
        form_layout.addRow("", self.modo_input)

        self.estado_input = self.create_disabled_input("Estado inicial")
        form_layout.addRow("", self.estado_input)

        form_widget = QWidget()
        form_widget.setLayout(form_layout)
        layout.addWidget(form_widget)

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

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.setSpacing(10)
        button_layout.addWidget(back_button)
        button_layout.addSpacerItem(QSpacerItem(15, 20, QSizePolicy.Fixed, QSizePolicy.Minimum))

        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        layout.addLayout(button_layout)

        self.setLayout(layout)

        if self.actuator_id is not None:
            self.load_actuator_data()

    def create_disabled_input(self, placeholder):
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        input_field.setFont(QFont("Candara", 10))
        input_field.setReadOnly(True)
        input_field.setStyleSheet("""
            QLineEdit {
                font: bold;
                color: #AAAAAA;
                background-color: #1E1B2E;
                padding: 10px;
                border: 2px solid #30EACE;
                border-radius: 20px;
            }
            QLineEdit::placeholder {
                color: #AAAAAA;
            }
        """)
        input_field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        return input_field

    def load_actuator_data(self):
        conn = connect_db()
        if conn:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT nombre, tipo, bus, address, modo_activacion, estado_inicial
                FROM actuadores
                WHERE id_actuador = %s
            """
            cursor.execute(query, (self.actuator_id,))
            row = cursor.fetchone()
            if row:
                self.name_input.setText(row['nombre'] or "")
                self.tipo_input.setText(row['tipo'] or "")
                self.bus_input.setText(str(row['bus'] or ""))
                self.address_input.setText(str(row['address'] or ""))
                self.modo_input.setText(row['modo_activacion'] or "")
                self.estado_input.setText("Encendido" if row['estado_inicial'] else "Apagado")
            cursor.close()
            conn.close()
        else:
            print("No se pudo conectar a la base de datos para cargar datos del actuador.")
