from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from views.seleccion_usuario import TitleBar
from views.about_sensor_modal import AboutSensorWidget
from models.database import connect_db

class SensorsAppAdmin(QWidget):
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
                margin-left: 3px;
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
        sensors_frame = QFrame()
        sensors_frame.setStyleSheet("background-color: #28243C; border-radius: 15px;")
        sensors_layout = QVBoxLayout(sensors_frame)
        sensors_layout.setContentsMargins(20, 40, 20, 20)


        # Buscar ícono según el nombre
        icon_path = "assets/icons/sensors-white.svg"

        # Icono PNG al lado izquierdo del nombre
        icon_label = QLabel()
        icon_pixmap = QPixmap(icon_path)

        if icon_pixmap.isNull():
            print(f"⚠️ No se pudo cargar el ícono: {icon_path}")

        # Escalar sin recortar
        icon_label.setPixmap(icon_pixmap.scaledToHeight(28, Qt.SmoothTransformation))
        icon_label.setContentsMargins(10, 0, 0, 0)
        icon_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        icon_label.setAlignment(Qt.AlignCenter)
        """icon_label.setStyleSheet("margin-right: 10px;")"""

        # --- Título ---
        title_sensores = QLabel("Sensores")
        title_sensores.setObjectName("Title")

        # --- Layout horizontal para título y botón ---
        top_layout = QHBoxLayout()
        top_layout.addWidget(icon_label)
        top_layout.addWidget(title_sensores, alignment=Qt.AlignVCenter)
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
        sensors_layout.addLayout(top_layout)

        # Espacio entre el título/botón y el listado de dispositivos
        space_between = QWidget()
        space_between.setFixedHeight(30)
        sensors_layout.addWidget(space_between)

        sensors_layout.addWidget(scroll_area)

        self.sensors_list_layout = QVBoxLayout(scroll_content)
        scroll_content.setContentsMargins(0, 0, 0, 0)
        scroll_area.setContentsMargins(0, 0, 0, 0)
        self.sensors_list_layout.setContentsMargins(10, 10, 10, 10)
        self.sensors_list_layout.setSpacing(30)

        scroll_area.setWidget(scroll_content)

        # --- Agregar widgets al layout ---
        sensors_layout.addLayout(top_layout)
        sensors_layout.addWidget(scroll_area)

        main_layout.addWidget(sensors_frame)

        # --- Llenar dispositivos de ejemplo ---
        self.populate_sensors()
        
    def add_sensor_card(self, sensor_id, nombre):
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
        sensor_frame = QFrame()
        sensor_frame.setStyleSheet("""
            background-color: #1f2232;
            border-radius: 35px;
        """)
        sensor_frame.setFixedHeight(70)
        sensor_layout = QHBoxLayout(sensor_frame)
        sensor_layout.setContentsMargins(20, 10, 20, 10)

        name_label = QLabel(nombre)
        name_label.setStyleSheet("color: white; font-weight: bold; font-size: 16px;")

        # Botones
        features_button = QPushButton("Características")
        features_button.setStyleSheet("""
            QPushButton {
                background-color: #0D2B23;
                color: white;
                font-weight: bold;
                border-radius: 14px;
                padding: 6px 14px;
                border: 1px solid #10B981;
            }
            QPushButton:hover {
                background-color: #218463;
            }
        """)
        features_button.clicked.connect(lambda _, sid=sensor_id: self.about_sensors(sid))

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        buttons_layout.addWidget(features_button)

        sensor_layout.addWidget(name_label)
        sensor_layout.addStretch()
        sensor_layout.addLayout(buttons_layout)

        # Asignar el interior al exterior
        outer_layout = QVBoxLayout(outer_frame)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(sensor_frame)

        # Agregar al layout principal
        self.sensors_list_layout.addWidget(outer_frame)

    def populate_sensors(self):

        self.sensores_icons = {
            "Sensor PH": "assets/img/ph.png",
            "Temperatura en el aire": "assets/img/temam.png",
            "Temperatura en el agua": "assets/img/tema.png",
            "Sensor de Humedad": "assets/img/hum.png",
            "Sensor de ORP": "assets/img/orp.png",
            "Sensor Ultrasónico": "assets/img/nivel.png"
        }


        conn = connect_db()
        if not conn:
            print("No se pudo conectar a la base de datos para cargar sensores.")
            return

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id_sensor, nombre FROM sensores")
        sensores = cursor.fetchall()

        for sensor in sensores:
            sensor_id = sensor['id_sensor']
            nombre = sensor['nombre']

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

            sensor_frame = QFrame()
            sensor_frame.setStyleSheet("""
                background-color: #1f2232;
                border-radius: 35px;
            """)
            sensor_frame.setFixedHeight(70)
            sensor_layout = QHBoxLayout(sensor_frame)
            sensor_layout.setContentsMargins(20, 10, 20, 10)

            # Buscar ícono según el nombre
            icon_path = self.sensores_icons.get(nombre, "assets/img/logo.png")

            # Icono PNG al lado izquierdo del nombre
            icon_label = QLabel()
            icon_pixmap = QPixmap(icon_path)

            if icon_pixmap.isNull():
                print(f"⚠️ No se pudo cargar el ícono: {icon_path}")

            # Escalar sin recortar
            icon_label.setPixmap(icon_pixmap.scaledToHeight(32, Qt.SmoothTransformation))
            icon_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            icon_label.setAlignment(Qt.AlignCenter)
            """icon_label.setStyleSheet("margin-right: 10px;")"""

            name_label = QLabel(nombre)
            name_label.setStyleSheet("color: white; font-weight: bold; font-size: 16px;")

            features_button = QPushButton("Características")
            features_button.setStyleSheet("""
                QPushButton {
                    background-color: #0D2B23;
                    color: white;
                    font-weight: bold;
                    border-radius: 14px;
                    padding: 6px 14px;
                    border: 1px solid #10B981;
                }
                QPushButton:hover {
                    background-color: #218463;
                }
            """)
            # Paso el id usando lambda para el callback
            features_button.clicked.connect(lambda _, sid=sensor_id: self.about_sensors(sid))

            buttons_layout = QHBoxLayout()
            buttons_layout.setSpacing(10)
            buttons_layout.addWidget(features_button)


            sensor_layout.addWidget(icon_label)
            sensor_layout.addWidget(name_label)
            sensor_layout.addStretch()
            sensor_layout.addLayout(buttons_layout)

            outer_layout = QVBoxLayout(outer_frame)
            outer_layout.setContentsMargins(0, 0, 0, 0)
            outer_layout.addWidget(sensor_frame)

            self.sensors_list_layout.addWidget(outer_frame)

        cursor.close()
        conn.close()

    def about_sensors(self, sensor_id):
        dialog = AboutSensorWidget(self.ventana_login, sensor_id)
        dialog.exec_()
        
    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()