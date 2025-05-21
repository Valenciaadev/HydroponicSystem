from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from views.seleccion_usuario import TitleBar
from views.about_actuator_modal import AboutActuatorWidget
from models.database import connect_db

class ActuatorsAppAdmin(QWidget):
    def __init__(self, ventana_login, embed=False):
        super().__init__(ventana_login)
        self.ventana_login = ventana_login
        self.conn = connect_db()
        if self.conn:
            self.cursor = self.conn.cursor(dictionary=True)
        else:
            print("No se pudo establecer la conexión a la base de datos.")
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QLabel#Title {
                font-size: 28px;
                font-weight: bold;
                color: white;
                margin-left: 15px;
            }
            QLabel#Subtitle {
                font-size: 16px;
                font-weight: bold;
                color: white;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 20px;
                background-color: #7FD1B9;
                color: black;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6fc9a9;
            }
        """)

        main_layout = QVBoxLayout(self)

        # --- Frame principal ---
        actuators_frame = QFrame()
        actuators_frame.setStyleSheet("background-color: #28243C; border-radius: 15px;")
        actuators_layout = QVBoxLayout(actuators_frame)
        actuators_layout.setContentsMargins(20, 40, 20, 20)

        # --- Título ---
        title_actuadores = QLabel("Actuadores")
        title_actuadores.setObjectName("Title")

        # --- Layout horizontal para título y botón ---
        top_layout = QHBoxLayout()
        top_layout.addWidget(title_actuadores, alignment=Qt.AlignVCenter)
        top_layout.addStretch()
        
        # --- Contenedor para los dispositivos ---
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
            }
            QScrollBar:vertical {
                width: 12px;
                background: #252535;
            }
            QScrollBar::handle:vertical {
                background: #4a4a5a;
                min-height: 20px;
                border-radius: 6px;
            }
        """)
        scroll_content = QWidget()
        scroll_content.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # --- Agregar widgets al layout ---
        actuators_layout.addLayout(top_layout)

        # Espacio entre el título/botón y el listado de dispositivos
        space_between = QWidget()
        space_between.setFixedHeight(30)
        actuators_layout.addWidget(space_between)

        actuators_layout.addWidget(scroll_area)

        self.actuators_list_layout = QVBoxLayout(scroll_content)
        scroll_content.setContentsMargins(0, 0, 0, 0)
        scroll_area.setContentsMargins(0, 0, 0, 0)
        self.actuators_list_layout.setContentsMargins(10, 10, 10, 10)
        self.actuators_list_layout.setSpacing(30)

        scroll_area.setWidget(scroll_content)

        # --- Agregar widgets al layout ---
        actuators_layout.addLayout(top_layout)
        actuators_layout.addWidget(scroll_area)

        main_layout.addWidget(actuators_frame)

        # --- Llenar dispositivos de ejemplo ---
        self.populate_actuators()
        
    def add_actuator_card(self, actuator_id, nombre):
        # --- Frame exterior ---
        outer_frame = QFrame()
        outer_frame.setFixedHeight(75)
        outer_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #60D4B8, stop:1 #1E2233);
                border-radius: 35px;
                padding: 2px;
            }
        """)

        # --- Frame interior ---
        actuator_frame = QFrame()
        actuator_frame.setStyleSheet("""
            background-color: #1f2232;
            border-radius: 35px;
        """)
        actuator_frame.setFixedHeight(70)
        actuator_layout = QHBoxLayout(actuator_frame)
        actuator_layout.setContentsMargins(20, 10, 20, 10)

        name_label = QLabel(nombre)
        name_label.setStyleSheet("color: white; font-weight: bold; font-size: 16px;")

        # Botones
        features_button = QPushButton("Características")
        features_button.setStyleSheet("""
            QPushButton {
                background-color: #7FD1B9;
                color: black;
                font-weight: bold;
                border-radius: 14px;
                padding: 6px 14px;
            }
            QPushButton:hover {
                background-color: #429E88;
            }
        """)
        features_button.clicked.connect(lambda _, sid=actuator_id: self.about_actuators(sid))

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        buttons_layout.addWidget(features_button)

        actuator_layout.addWidget(name_label)
        actuator_layout.addStretch()
        actuator_layout.addLayout(buttons_layout)

        # Asignar el interior al exterior
        outer_layout = QVBoxLayout(outer_frame)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(actuator_frame)

        # Agregar al layout principal
        self.actuators_list_layout.addWidget(outer_frame)

    def populate_actuators(self):
        conn = connect_db()
        if not conn:
            print("No se pudo conectar a la base de datos para cargar actuadores.")
            return

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id_actuador, nombre FROM actuadores")
        actuadores = cursor.fetchall()

        for actuador in actuadores:
            actuador_id = actuador['id_actuador']
            nombre = actuador['nombre']

            outer_frame = QFrame()
            outer_frame.setFixedHeight(75)
            outer_frame.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #60D4B8, stop:1 #1E2233);
                    border-radius: 35px;
                    padding: 2px;
                }
            """)

            actuador_frame = QFrame()
            actuador_frame.setStyleSheet("""
                background-color: #1f2232;
                border-radius: 35px;
            """)
            actuador_frame.setFixedHeight(70)
            actuador_layout = QHBoxLayout(actuador_frame)
            actuador_layout.setContentsMargins(20, 10, 20, 10)

            name_label = QLabel(nombre)
            name_label.setStyleSheet("color: white; font-weight: bold; font-size: 16px;")

            features_button = QPushButton("Características")
            features_button.setStyleSheet("""
                QPushButton {
                    background-color: #7FD1B9;
                    color: black;
                    font-weight: bold;
                    border-radius: 14px;
                    padding: 6px 14px;
                }
                QPushButton:hover {
                    background-color: #429E88;
                }
            """)
            # Paso el id usando lambda para el callback
            features_button.clicked.connect(lambda _, sid=actuador_id: self.about_actuators(sid))

            buttons_layout = QHBoxLayout()
            buttons_layout.setSpacing(10)
            buttons_layout.addWidget(features_button)

            actuador_layout.addWidget(name_label)
            actuador_layout.addStretch()
            actuador_layout.addLayout(buttons_layout)

            outer_layout = QVBoxLayout(outer_frame)
            outer_layout.setContentsMargins(0, 0, 0, 0)
            outer_layout.addWidget(actuador_frame)

            self.actuators_list_layout.addWidget(outer_frame)

        cursor.close()
        conn.close()

    def about_actuators(self, actuador_id):
        dialog = AboutActuatorWidget(self.ventana_login, actuador_id)
        dialog.exec_()
        
    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()