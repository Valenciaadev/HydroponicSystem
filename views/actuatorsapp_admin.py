from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from views.seleccion_usuario import TitleBar
from views.about_actuator_modal import AboutActuatorWidget
from views.actuator_managment_modal import ActuatorManagmentWidget
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
        
    def add_actuator_card(self, actuator_id, nombre, tipo):
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
        features_button.clicked.connect(lambda _, sid=actuator_id: self.about_actuators(sid))

        if tipo == "Bomba peristáltica":
            gestionar_button = QPushButton("Gestionar dosis")
            gestionar_button.setStyleSheet("""
                QPushButton {
                    background-color: #2B2300;
                    color: white;
                    font-weight: bold;
                    border-radius: 14px;
                    padding: 6px 14px;
                    border: 1px solid #F59E0B;
                }
                QPushButton:hover {
                    background-color: #B88417;
                }
            """)
            
            # Aquí podrías conectar a una función que abra un modal para gestionar dosis
            gestionar_button.clicked.connect(lambda _, sid=actuator_id: self.actuators_managment(sid))

            buttons_layout = QHBoxLayout()
            buttons_layout.setSpacing(10)
            buttons_layout.addWidget(gestionar_button)
            buttons_layout.addWidget(features_button)
        
        else:
            toggle_button = QPushButton("Encender")
            toggle_button.setCheckable(True)  # Para que mantenga estado presionado
            toggle_button.setStyleSheet("""
                QPushButton {
                    background-color: #1E1B2E;
                    color: white;
                    font-weight: bold;
                    border-radius: 14px;
                    padding: 6px 14px;
                    width: 98px;
                    border: 1px solid #2563EB;
                }
                QPushButton:hover {
                    background-color: #1A3699;
                }
            """)
            
            def toggle_state():
                if toggle_button.isChecked():
                    toggle_button.setText("Apagar")
                    toggle_button.setStyleSheet("""
                        QPushButton {
                            background-color: #3A1212;
                            color: white;
                            font-weight: bold;
                            border-radius: 14px;
                            padding: 6px 14px;
                            width: 98px;
                            border: 1px solid #DC2626;
                        }
                        QPushButton:hover {
                            background-color: #8B1E1E;
                        }
                    """)
                    self.update_estado(actuator_id, 1)
                    print(f"{nombre} encendido")
                else:
                    toggle_button.setText("Encender")
                    toggle_button.setStyleSheet("""
                        QPushButton {
                            background-color: #1E1B2E;
                            color: white;
                            font-weight: bold;
                            border-radius: 14px;
                            padding: 6px 14px;
                            width: 98px;
                            border: 1px solid #2563EB;
                        }
                        QPushButton:hover {
                            background-color: #1A3699;
                        }
                    """)
                    self.update_estado(actuator_id, 0)
                    print(f"{nombre} apagado")

            toggle_button.clicked.connect(toggle_state)
            
            buttons_layout = QHBoxLayout()
            buttons_layout.setSpacing(10)
            buttons_layout.addWidget(toggle_button)
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
        if not self.conn or not self.cursor:
            print("No se pudo conectar a la base de datos para cargar actuadores.")
            return

        self.cursor.execute("SELECT id_actuador, nombre, tipo FROM actuadores")
        actuadores = self.cursor.fetchall()

        for actuador in actuadores:
            self.add_actuator_card(
                actuador['id_actuador'], 
                actuador['nombre'], 
                actuador['tipo']
            )

    def about_actuators(self, actuador_id):
        dialog = AboutActuatorWidget(self.ventana_login, actuador_id)
        dialog.exec_()
        
    def actuators_managment(self, actuador_id):
        dialog = ActuatorManagmentWidget(self.ventana_login, actuador_id)
        dialog.exec_()
        
    def update_estado(self, actuator_id, nuevo_estado):
        try:
            self.cursor.execute(
                "UPDATE actuadores SET estado_actual = %s WHERE id_actuador = %s",
                (nuevo_estado, actuator_id)
            )
            self.conn.commit()
            print(f"Estado del actuador {actuator_id} actualizado a {nuevo_estado}")
        except Exception as e:
            print("Error al actualizar el estado del actuador:", e)
        
    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()