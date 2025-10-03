from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from models.database import get_hortalizas, update_hortaliza_seleccion, get_sensors_data
from PyQt5.QtCore import pyqtSignal


class GestionHortalizasAppAdmin(QWidget):
    crop_changed = pyqtSignal(int)
    def __init__(self, ventana_login, embed=None):
        super().__init__(ventana_login)
        self.ventana_login = ventana_login
        self.current_expanded = None
        self.arrow_buttons = {}
        self.details_frames = {}
        self.dialog = None  # Referencia al diálogo de selección
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
            QPushButton:checked {
                background-color: #546A7B;
                border-left: 5px solid #D4F5F5;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # --- Frame principal ---
        main_frame = QFrame()
        main_frame.setStyleSheet("background-color: #27243A; border-radius: 10px;")
        main_frame.setContentsMargins(20, 10, 20, 20)

        frame_layout = QVBoxLayout(main_frame)

        # --- Título y botón de selección ---
        title_filter_layout = QHBoxLayout()
        
        # Icono
        icon_label = QLabel()
        icon_pixmap = QPixmap("assets/icons/sapling.svg")
        if not icon_pixmap.isNull():
            icon_label.setPixmap(icon_pixmap.scaledToHeight(28, Qt.SmoothTransformation))
        icon_label.setContentsMargins(10, 0, 0, 0)
        icon_label.setAlignment(Qt.AlignCenter)

        title_label = QLabel("Gestión de Hortalizas")
        title_label.setObjectName("Title")
        title_filter_layout.addWidget(icon_label)
        title_filter_layout.addWidget(title_label)
        title_filter_layout.addStretch()

        # Botón para seleccionar cultivo
        self.select_crop_frame = QFrame()
        self.select_crop_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #60D4B8, stop:1 #1E2233);
                border-radius: 0px;
                padding: 2px; 
            }
        """)

        self.select_crop_button = QPushButton("Selecciona tu cultivo")
        self.select_crop_button.setCursor(Qt.PointingHandCursor)
        self.select_crop_button.setStyleSheet("""
            QPushButton {
                background-color: #1F2232;
                color: white;
                font-weight: bold;
                font-size: 16px;
                border: none;
                padding: 10px 20px;
                border-radius: 0px;
            }
            QPushButton:hover {
                background-color: #2B2E3F;
            }
        """)
        self.select_crop_button.clicked.connect(self.show_crop_selection_dialog)
        
        select_crop_layout = QHBoxLayout(self.select_crop_frame)
        select_crop_layout.setContentsMargins(0, 0, 0, 0)
        select_crop_layout.addWidget(self.select_crop_button)
        
        title_filter_layout.addWidget(self.select_crop_frame)
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
        self.update_button_text()

    def show_crop_selection_dialog(self):
        self.dialog = QDialog(self)  # Guardar referencia
        self.dialog.setWindowTitle("Seleccionar cultivo")
        self.dialog.setMinimumSize(400, 500)
        self.dialog.setStyleSheet("""
            QDialog {
                background-color: #1E1B2E;
                border-radius: 15px;
            }
        """)
        
        layout = QVBoxLayout(self.dialog)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title_label = QLabel("Selecciona tu cultivo")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 22px; 
            font-weight: bold; 
            color: #60D4B8; 
            margin-bottom: 20px;
        """)
        layout.addWidget(title_label)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none; background: transparent;")
        
        self.scroll_content_dialog = QWidget()
        self.scroll_layout_dialog = QVBoxLayout(self.scroll_content_dialog)
        self.scroll_layout_dialog.setContentsMargins(5, 5, 5, 5)
        self.scroll_layout_dialog.setSpacing(10)
        
        self.load_crop_buttons()
        
        scroll_area.setWidget(self.scroll_content_dialog)
        layout.addWidget(scroll_area)
        
        self.dialog.exec_()
    
    def load_crop_buttons(self):
        # Limpiar layout primero
        for i in reversed(range(self.scroll_layout_dialog.count())): 
            widget = self.scroll_layout_dialog.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        hortalizas = get_hortalizas()
        
        for hortaliza in hortalizas:
            btn = QPushButton(hortaliza['nombre'])
            btn.setCheckable(True)
            btn.setChecked(hortaliza['seleccion'] == 1)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #27243A;
                    color: white;
                    font-size: 16px;
                    padding: 15px;
                    border-radius: 10px;
                    text-align: center;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #3A3750;
                }
                QPushButton:checked {
                    background-color: #546A7B;
                    border-left: 5px solid #D4F5F5;
                }
            """)
            btn.clicked.connect(lambda _, h_id=hortaliza['id_hortaliza']: self.handle_crop_selection(h_id))
            self.scroll_layout_dialog.addWidget(btn)
        
        self.scroll_layout_dialog.addStretch()

    def handle_crop_selection(self, hortaliza_id):
        # Cerrar diálogo principal
        if self.dialog:
            self.dialog.close()
        
        # Actualizar UI inmediatamente
        self.update_ui_for_selection(hortaliza_id)
        
        # Actualizar BD en segundo plano
        QTimer.singleShot(0, lambda: self.finalize_db_update(hortaliza_id))

    def update_ui_for_selection(self, hortaliza_id):
        # Actualizar estilo de todas las tarjetas
        for i in range(self.hortalizas_layout.count()):
            item = self.hortalizas_layout.itemAt(i)
            if item.widget() and hasattr(item.widget(), 'hortaliza_id'):
                frame = item.widget().findChild(QFrame)
                if frame:
                    selected = (item.widget().hortaliza_id == hortaliza_id)
                    frame.setProperty("selected", "true" if selected else "false")
                    frame.style().unpolish(frame)
                    frame.style().polish(frame)
        
        # Actualizar texto del botón principal
        self.select_crop_button.setText("Cambiar de cultivo")
        self.update()

    def finalize_db_update(self, hortaliza_id):
        success = update_hortaliza_seleccion(hortaliza_id)
        if success:
            # Actualiza lista y botón
            self.load_hortalizas()
            self.update_button_text()
            # Notifica a la vista de inicio para refrescar tooltips
            self.crop_changed.emit(hortaliza_id)
        else:
            # Revertir cambios si falla la BD
            self.load_hortalizas()
            self.update_button_text()


    def update_button_text(self):
        hortalizas = get_hortalizas()
        selected = any(h['seleccion'] == 1 for h in hortalizas)
        self.select_crop_button.setText("Cambiar de cultivo" if selected else "Selecciona tu cultivo")

    def load_hortalizas(self):
        self.clear_layout(self.hortalizas_layout)
        
        hortalizas = get_hortalizas()
        for hortaliza in hortalizas:
            self.add_hortaliza_card(hortaliza['id_hortaliza'], hortaliza['nombre'], hortaliza['seleccion'])

    def add_hortaliza_card(self, hortaliza_id, nombre, seleccionada, details_height=250):
        hortaliza_icons = {
            "Lechuga": "assets/img/lechuga.png",
            "Espinaca": "assets/img/espinacas.png",
            "Acelga": "assets/img/acelga.png",
            "Rúcula": "assets/img/rucula.png",
            "Albahaca": "assets/img/albahaca.png",
            "Mostaza": "assets/img/mostaza.png"
        }
        
        apodos = {
            "Sensor PH": " ph",
            "Temperatura en el aire": " °C",
            "Temperatura en el agua": " °C",
            "Sensor de Humedad": " %",
            "Sensor de ORP": " mV",
            "Sensor Ultrasónico": " cm"
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
        card_frame.hortaliza_id = hortaliza_id  # Guardar referencia

        # --- Interior de la tarjeta ---
        inner_frame = QFrame()
        inner_frame.setStyleSheet("""
            QFrame {
                background-color: #1f2232;
                border-radius: 35px;
            }
            QFrame[selected="true"] {
                background-color: #2a3a4a;
                border: 2px solid #60D4B8;
            }
        """)
        inner_frame.setProperty("selected", "true" if seleccionada else "false")
        inner_frame.setFixedHeight(70)

        inner_layout = QHBoxLayout(inner_frame)
        inner_layout.setContentsMargins(20, 10, 20, 10)

        # Icono
        icon_label = QLabel()
        icon_path = hortaliza_icons.get(nombre, "assets/img/logo.png")
        icon_pixmap = QPixmap(icon_path)
        if not icon_pixmap.isNull():
            icon_label.setPixmap(icon_pixmap.scaledToHeight(32, Qt.SmoothTransformation))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("background: transparent;")

        name_label = QLabel(nombre)
        name_label.setStyleSheet("""
            QLabel {
                background: transparent;
                color: white;
                font-weight: bold;
                font-size: 16px;
            }
        """)

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
        details_frame.setFixedHeight(250)

        details_layout = QVBoxLayout(details_frame)
        details_layout.setSpacing(15)

        try:
            sensores_data = get_sensors_data(hortaliza_id) or []
        except Exception as e:
            print(f"Error al obtener sensores: {e}")
            sensores_data = []

        # Contenedor para sensores
        sensors_container = QWidget()
        sensors_layout = QHBoxLayout(sensors_container)
        sensors_layout.setContentsMargins(0, 0, 0, 0)
        sensors_layout.setSpacing(15)

        for sensor in sensores_data:
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
                    font-size: 18px;
                    margin-bottom: 5px;
                }
                QLabel#range_label {
                    font-size: 16px;
                    margin-bottom: 3px;
                }
                QLabel#range_values {
                    font-size: 16px;
                }
            """)
            sensor_card.setFixedHeight(210)

            card_layout = QVBoxLayout(sensor_card)
            card_layout.setContentsMargins(0, 0, 0, 0)
            card_layout.setSpacing(0)

            name_label = QLabel(sensor.get('nombre', 'Sensor'))
            name_label.setObjectName("sensor_name")
            name_label.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(name_label)

            range_label = QLabel("Rango óptimo")
            range_label.setObjectName("range_label")
            range_label.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(range_label)

            apodo = apodos.get(sensor.get('nombre', ''), "")
            values_label = QLabel(f"{sensor.get('rango_min', 0)}{apodo} - {sensor.get('rango_max', 0)}{apodo}")
            values_label.setObjectName("range_values")
            values_label.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(values_label)

            card_layout.addStretch()
            sensors_layout.addWidget(sensor_card)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(sensors_container)
        scroll_area.setStyleSheet("border: none; background: transparent;")
        scroll_area.setMinimumHeight(240)

        details_layout.addWidget(scroll_area)
        details_layout.addStretch()

        self.hortalizas_layout.addWidget(card_frame)
        self.hortalizas_layout.addWidget(details_frame)

        # Guardar referencias
        self.arrow_buttons[hortaliza_id] = arrow_button
        self.details_frames[hortaliza_id] = details_frame

        arrow_button.clicked.connect(lambda _, h_id=hortaliza_id: self.toggle_details(h_id))

    def toggle_details(self, hortaliza_id):
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

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout(child.layout())