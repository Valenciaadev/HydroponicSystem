from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from models.database import get_hortalizas, update_hortaliza_seleccion, get_sensors_data, get_sensor_ranges

class GestionHortalizasAppAdmin(QWidget):
    def __init__(self, ventana_login, embed=None):
        super().__init__(ventana_login)
        self.ventana_login = ventana_login
        self.current_expanded = None
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QLabel#Title {
                font-size: 32px;
                font-weight: bold;
                color: white;
                margin-top: 20px;
                margin-bottom: 20px;
                font-family: 'Candara';
            }
            QLabel#Subtitle {
                font-size: 22px;
                font-weight: bold;
                color: white;
                margin-top: 10px;
                font-family: 'Candara';
            }
            QPushButton {
                padding: 5px 10px;
                border-radius: 10px;
                background-color: #4A90E2;
                color: white;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
            QComboBox {
                padding: 5px 10px;
                border: 2px solid #60D4B8;
                border-radius: 10px;
                background-color: #1E1E2E;
                color: white;
                min-width: 150px;
            }
        """)

        layout = QVBoxLayout(self)

        # --- Frame principal ---
        main_frame = QFrame()
        main_frame.setStyleSheet("background-color: #27243A; border-radius: 10px;")
        main_frame.setContentsMargins(20, 10, 20, 20)

        frame_layout = QVBoxLayout(main_frame)

        # --- Título y filtro ---
        title_filter_layout = QHBoxLayout()
        

        # Buscar ícono según el nombre
        icon_path = "assets/icons/sapling.svg"

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

        title_label = QLabel("Gestión de Hortalizas")
        title_label.setObjectName("Title")
        title_filter_layout.addWidget(icon_label)
        title_filter_layout.addWidget(title_label)
        title_filter_layout.addStretch()  # Mueve el combo a la derecha

        self.hortalizas_combo = QComboBox()
        self.hortalizas_combo.currentIndexChanged.connect(self.on_hortaliza_selected)
        title_filter_layout.addWidget(self.hortalizas_combo)

        frame_layout.addLayout(title_filter_layout)

        # --- Scroll Area para las hortalizas ---
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
        
        self.scroll_content = QWidget()
        self.scroll_content.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.hortalizas_layout = QVBoxLayout(self.scroll_content)
        self.hortalizas_layout.setContentsMargins(10, 10, 10, 10)
        self.hortalizas_layout.setSpacing(15)
        
        scroll_area.setWidget(self.scroll_content)
        frame_layout.addWidget(scroll_area)

        layout.addWidget(main_frame)
        
        # Cargar datos
        self.load_hortalizas()

    def load_hortalizas(self):
        # Evitar loop desconectando temporalmente la señal
        self.hortalizas_combo.blockSignals(True)
        self.hortalizas_combo.clear()
        self.clear_layout(self.hortalizas_layout)
        
        hortalizas = get_hortalizas()
        if not hortalizas:
            self.hortalizas_combo.blockSignals(False)
            return
            
        for hortaliza in hortalizas:
            self.hortalizas_combo.addItem(hortaliza['nombre'], hortaliza['id_hortaliza'])
            self.add_hortaliza_card(hortaliza['id_hortaliza'], hortaliza['nombre'], hortaliza['seleccion'])

        self.hortalizas_combo.blockSignals(False)

    def add_hortaliza_card(self, hortaliza_id, nombre, seleccionada, details_height=250):

        self.hortaliza_icons = {
            "Lechuga": "assets/img/lechuga.png",
            "Espinaca": "assets/img/espinacas.png",
            "Acelga": "assets/img/acelga.png",
            "Rúcula": "assets/img/rucula.png",
            "Albahaca": "assets/img/albahaca.png",
            "Mostaza": "assets/img/mostaza.png"
        }

        # --- Frame de tarjeta ---
        card_frame = QFrame()
        card_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #60D4B8, stop:1 #1E2233);
                border-radius: 35px;
                padding: 2px;
            }
        """)
        card_layout = QVBoxLayout(card_frame)
        card_layout.setContentsMargins(0, 0, 0, 0)

        # --- Interior de la tarjeta ---
        inner_frame = QFrame()
        inner_frame.setStyleSheet("background-color: #1f2232; border-radius: 35px;")
        inner_frame.setFixedHeight(70)

        inner_layout = QHBoxLayout(inner_frame)
        inner_layout.setContentsMargins(20, 10, 20, 10)

        # Buscar ícono según el nombre
        icon_path = self.hortaliza_icons.get(nombre, "assets/img/logo.png")

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

        arrow_button = QPushButton()
        arrow_button.setIcon(QIcon("assets/icons/bxs-down-arrow.svg"))
        arrow_button.setFixedSize(30, 30)
        arrow_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: #444;
                border-radius: 15px;
            }
        """)

                # Agregar al layout
        inner_layout.addWidget(icon_label)
        inner_layout.addWidget(name_label)
        inner_layout.addStretch()
        inner_layout.addWidget(arrow_button)

        card_layout.addWidget(inner_frame)

        # --- Frame de detalles ---
        details_frame = QFrame()
        details_frame.setStyleSheet("background-color: #1f2232; border-radius: 10px;")
        details_frame.setContentsMargins(10, 0, 10, 0)
        details_frame.setVisible(False)
        details_frame.setFixedHeight(details_height)

        # Layout principal para los detalles
        details_layout = QVBoxLayout(details_frame)
        details_layout.setSpacing(15)

        # OPCIÓN 1: Obtener todos los sensores de una vez (recomendado)
        try:
            sensores_data = get_sensors_data(hortaliza_id)
            if not sensores_data:
                raise Exception("No se encontraron datos de sensores")
        except Exception as e:
            print(f"Error al obtener datos de sensores (usando get_sensors_data): {e}")
            # Datos de respaldo
            sensores_data = [
                {"id": 1, "nombre": "Sensor de PH", "rango_min": 0, "rango_max": 0},
                {"id": 2, "nombre": "Temp. Aire", "rango_min": 0, "rango_max": 0},
                {"id": 3, "nombre": "Temp. Agua", "rango_min": 0, "rango_max": 0},
                {"id": 4, "nombre": "Sensor de Humedad", "rango_min": 0, "rango_max": 0},
                {"id": 5, "nombre": "Sensor de ORP", "rango_min": 0, "rango_max": 0},
                {"id": 6, "nombre": "Sensor Ultrasónico", "rango_min": 0, "rango_max": 0}
            ]

        # OPCIÓN ALTERNATIVA: Si la opción 1 no funciona, usa esta (descomenta)
        """
        sensores_base = [
            {"id": 1, "nombre": "Sensor PH"},
            {"id": 2, "nombre": "Temp. Aire"},
            {"id": 3, "nombre": "Temp. Agua"},
            {"id": 4, "nombre": "Humedad"},
            {"id": 5, "nombre": "ORP"},
            {"id": 6, "nombre": "Ultrasónico"}
        ]
        
        sensores_data = []
        for sensor in sensores_base:
            try:
                ranges = get_sensor_ranges(hortaliza_id, sensor["id"])
                sensores_data.append({
                    "id": sensor["id"],
                    "nombre": sensor["nombre"],
                    "rango_min": ranges["min"],
                    "rango_max": ranges["max"]
                })
            except Exception as e:
                print(f"Error al obtener rangos para sensor {sensor['id']}: {e}")
                sensores_data.append({
                    "id": sensor["id"],
                    "nombre": sensor["nombre"],
                    "rango_min": 0,
                    "rango_max": 0
                })
        """

        # Contenedor para las cartas
        cards_container = QWidget()
        cards_layout = QHBoxLayout(cards_container)
        cards_layout.setContentsMargins(0, 0, 0, 0)
        cards_layout.setSpacing(15)

        for sensor in sensores_data:
            # Crear carta para cada sensor
            sensor_card = QFrame()
            sensor_card.setStyleSheet("""
                QFrame {
                    background-color: #27243A;
                    border-radius: 15px;
                    padding: 15px;
                    min-width: 180px;
                }
                QLabel {
                    color: white;
                }
                QLabel#sensor_name {
                    font-weight: bold;
                    color: #ffffff;
                    font-size: 18px;
                    margin-bottom: 5px;
                    margin-top: 5px;
                }
                QLabel#range_text {
                    font-weight: semi-bold;
                    color: #ffffff;
                    font-size: 16px;
                }
                QLabel#range_values {
                    font-weight: semi-bold;
                    color: #ffffff;
                    font-size: 16px;
                    margin-top: 3px;

                }
            """)
            sensor_card.setFixedHeight(210)

            sensor_layout = QVBoxLayout(sensor_card)
            sensor_layout.setContentsMargins(0, 0, 0, 0)
            sensor_layout.setSpacing(0)

            # Nombre del sensor
            name_label = QLabel(sensor["nombre"])
            name_label.setObjectName("sensor_name")
            name_label.setAlignment(Qt.AlignCenter)
            sensor_layout.addWidget(name_label)

            # Texto "Rango óptimo"
            range_text = QLabel("Rango óptimo")
            range_text.setObjectName("range_text")
            range_text.setAlignment(Qt.AlignCenter)
            sensor_layout.addWidget(range_text)

            # Valores del rango
            range_values = QLabel(f"{sensor['rango_min']} - {sensor['rango_max']}")
            range_values.setObjectName("range_values")
            range_values.setAlignment(Qt.AlignCenter)
            sensor_layout.addWidget(range_values)

            sensor_layout.addStretch()
            cards_layout.addWidget(sensor_card)

        # Scroll area horizontal para las cartas
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(cards_container)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:horizontal {
                height: 10px;
                background: #252535;
                margin: 0 10px;
            }
            QScrollBar::handle:horizontal {
                background: #60D4B8;
                min-width: 30px;
                border-radius: 5px;
            }
        """)
        scroll_area.setMinimumHeight(240)

        details_layout.addWidget(scroll_area)
        details_layout.addStretch()

        self.hortalizas_layout.addWidget(card_frame)
        self.hortalizas_layout.addWidget(details_frame)

        self.arrow_buttons = getattr(self, 'arrow_buttons', {})
        self.details_frames = getattr(self, 'details_frames', {})
        self.arrow_buttons[hortaliza_id] = arrow_button
        self.details_frames[hortaliza_id] = details_frame

        arrow_button.clicked.connect(lambda _, h_id=hortaliza_id: self.toggle_hortaliza_details(h_id))

    def toggle_hortaliza_details(self, hortaliza_id):
        for h_id, frame in self.details_frames.items():
            button = self.arrow_buttons[h_id]
            if h_id == hortaliza_id:
                if frame.isVisible():
                    frame.hide()
                    button.setIcon(QIcon("assets/icons/bxs-down-arrow.svg"))
                    self.current_expanded = None
                else:
                    frame.show()
                    button.setIcon(QIcon("assets/icons/bxs-up-arrow.svg"))
                    self.current_expanded = h_id
            else:
                frame.hide()
                button.setIcon(QIcon("assets/icons/bxs-down-arrow.svg"))


    def on_hortaliza_selected(self, index):
        hortaliza_id = self.hortalizas_combo.itemData(index)
        if hortaliza_id:
            update_hortaliza_seleccion(hortaliza_id)
            # Recargar para actualizar visualmente
            self.load_hortalizas()

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout(child.layout())