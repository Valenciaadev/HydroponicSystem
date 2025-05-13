from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QScrollArea, QSizePolicy, QDialog, QLineEdit, QFormLayout )
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QSize
from views.seleccion_usuario import TitleBar
from views.create_sensor_modal import CreateSensorWidget
from views.about_sensor_modal import AboutSensorWidget

class SensorsAppAdmin(QWidget):
    def __init__(self, ventana_login, embed=False):
        super().__init__(ventana_login)
        self.ventana_login = ventana_login
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
        sensors_frame = QFrame()
        sensors_frame.setStyleSheet("background-color: #28243C; border-radius: 15px;")
        sensors_layout = QVBoxLayout(sensors_frame)
        sensors_layout.setContentsMargins(20, 40, 20, 20)

        # --- Título ---
        title_sensores = QLabel("Sensores")
        title_sensores.setObjectName("Title")

        # --- Botón añadir dispositivo con borde degradado ajustado ---
        self.add_sensor_button = QPushButton("Agregar sensor")
        self.add_sensor_button.setStyleSheet("""
            QPushButton {
                background-color: #1F2232;
                color: white;
                font-weight: bold;
                font-size: 16px;
                border: none;
                padding: 10px 20px;
                border-radius: 30px;
            }
            QPushButton:hover {
                background-color: #1F2F32;
            }
        """)

        self.add_sensor_button.clicked.connect(self.create_sensor)

        add_sensor_outer_frame = QFrame()
        add_sensor_outer_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #60D4B8, stop:1 #1E2233);
                border-radius: 30px;
                padding: 4px;
            }
        """)

        add_sensor_inner_layout = QVBoxLayout(add_sensor_outer_frame)
        add_sensor_inner_layout.setContentsMargins(0, 0, 0, 0)
        add_sensor_inner_layout.addWidget(self.add_sensor_button)

        # Ajusta el tamaño automáticamente
        add_sensor_outer_frame.setSizePolicy(self.add_sensor_button.sizePolicy())

        # --- Layout horizontal para título y botón ---
        top_layout = QHBoxLayout()
        top_layout.addWidget(title_sensores, alignment=Qt.AlignVCenter)
        top_layout.addStretch()
        top_layout.addWidget(add_sensor_outer_frame)
        
        # --- Contenedor para los dispositivos ---
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none;")
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

    def populate_sensors(self):
        sensores = ["Sensor A", "Sensor B", "Sensor C"]

        for nombre in sensores:
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
            features_button.clicked.connect(self.about_sensors)

            # shutdown_button = QPushButton("Apagar")
            # shutdown_button.setStyleSheet("""
            #     QPushButton {
            #         background-color: #FF6B6B;
            #         color: white;
            #         font-weight: bold;
            #         border-radius: 14px;
            #         padding: 6px 14px;
            #     }
            #     QPushButton:hover {
            #         background-color: #e85c5c;
            #     }
            # """)

            buttons_layout = QHBoxLayout()
            buttons_layout.setSpacing(10)
            buttons_layout.addWidget(features_button)
            # buttons_layout.addWidget(shutdown_button)

            sensor_layout.addWidget(name_label)
            sensor_layout.addStretch()
            sensor_layout.addLayout(buttons_layout)

            # Asignar el interior al exterior
            outer_layout = QVBoxLayout(outer_frame)
            outer_layout.setContentsMargins(0, 0, 0, 0)
            outer_layout.addWidget(sensor_frame)

            # Agregar al layout principal
            self.sensors_list_layout.addWidget(outer_frame)
    
    def create_sensor(self):
        dialog = CreateSensorWidget(self) 
        dialog.exec_()

    def about_sensors(self):
        dialog = AboutSensorWidget(self)
        dialog.exec_()