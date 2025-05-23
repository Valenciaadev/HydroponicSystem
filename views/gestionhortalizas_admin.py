from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from models.database import get_hortalizas, update_hortaliza_seleccion

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
                margin-left: 10px;
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
        
        title_label = QLabel("Gestión de Hortalizas")
        title_label.setObjectName("Title")
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

        inner_layout.addWidget(name_label)
        inner_layout.addStretch()
        inner_layout.addWidget(arrow_button)

        card_layout.addWidget(inner_frame)

        # --- Frame de detalles ---
        details_frame = QFrame()
        details_frame.setStyleSheet("background-color: #1f2232; border-radius: 10px;")
        details_frame.setVisible(False)
        details_frame.setFixedHeight(details_height)  # ← aquí controlas la altura

        details_layout = QVBoxLayout(details_frame)
        details_layout.setContentsMargins(20, 20, 20, 20)

        details_label = QLabel(f"Configuración para {nombre}")
        details_label.setStyleSheet("color: white;")
        details_layout.addWidget(details_label)

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