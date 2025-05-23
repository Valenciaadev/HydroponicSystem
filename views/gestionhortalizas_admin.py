from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class GestionHortalizasAppAdmin(QWidget):
    def __init__(self, ventana_login, embed=None):
        super().__init__(ventana_login)
        self.ventana_login = ventana_login
        self.init_ui()

    def init_ui(self):
        # Configuración base del widget (igual que HistoryAppAdmin)
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
        """)

        # Layout principal (igual que HistoryAppAdmin)
        layout = QVBoxLayout(self)

        # --- Frame principal ---
        main_frame = QFrame()
        main_frame.setStyleSheet("background-color: #27243A; border-radius: 10px;")
        main_frame.setContentsMargins(20, 10, 20, 20)
        frame_layout = QVBoxLayout(main_frame)

        # --- Título ---
        title_label = QLabel("Gestión de Hortalizas")
        title_label.setObjectName("Title")
        frame_layout.addWidget(title_label)

        # --- Aquí agregarías tus widgets específicos ---
        #Cositas
        
        # Espaciador para empujar contenido hacia arriba
        frame_layout.addStretch()

        # Añadir frame al layout principal (diferente a HistoryAppAdmin)
        layout.addWidget(main_frame)