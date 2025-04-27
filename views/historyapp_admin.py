""" from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class HistoryAppAdmin(QWidget):
    def __init__(self, ventana_login, embed=False):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("Pantalla de Historial")
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Candara", 16))
        layout.addWidget(label)
        self.setLayout(layout) """

from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QHBoxLayout, QFrame, QHeaderView
)
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QBrush
from PyQt5.QtCore import Qt


class HistoryAppAdmin(QWidget):
    def __init__(self, ventana_login, embed=None):
        super().__init__(ventana_login)
        self.ventana_login = ventana_login
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QLabel#Title {
                font-size: 20px;
                font-weight: bold;
                color: white;
            }
            QLabel#Subtitle {
                font-size: 16px;
                font-weight: bold;
                color: white;
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
                padding: 5px;
                border-radius: 10px;
                background-color: #2E2E3A;
                color: white;
            }
            QTableWidget {
                gridline-color: #7FD1B9;
                color: white;
                border: none;
                overflow: hidden; 
            }
        """)

        layout = QVBoxLayout(self)

        # --- Cuadro Historial ---
        historial_frame = QFrame()
        historial_frame.setStyleSheet("background-color: #27243A; border-radius: 15px;")
        historial_layout = QVBoxLayout(historial_frame)

        title_historial = QLabel("Historial")
        title_historial.setObjectName("Title")

        top_buttons_layout = QHBoxLayout()
        top_buttons_layout.addStretch()

        self.pdf_button = QPushButton()
        self.pdf_button.setIcon(QIcon("assets/icons/home-white.svg")) 
        self.pdf_button.setFixedSize(40, 40)  
        self.pdf_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                margin-right: 5px;

            }
            QPushButton:hover {
                background-color: #444;
                border-radius: 20px;
            }
        """)

        self.filter_combo = QComboBox()
        self.filter_combo.setStyleSheet("""
            QComboBox {
                padding: 5px 10px;
                border: 2px solid #4A90E2;
                border-radius: 10px;
                background-color: #1E1E2E;
                color: white;
                margin-right: 5px;
            }
            QComboBox:hover {
                border-color: #357ABD;
            }
            QComboBox QAbstractItemView {
                background-color: #1E1E2E;
                color: white;
                selection-background-color: #357ABD;
                selection-color: white;
            }
            QComboBox QAbstractItemView::item:hover {
                font-weight: bold; 
            }
        """)

        self.filter_combo.addItems([
            "Todo", "Mes anterior", "Último trimestre", "Último semestre", "Último año"
        ])

        top_buttons_layout.addWidget(self.pdf_button)
        top_buttons_layout.addWidget(self.filter_combo)

        # --- Cuadro Tabla dentro del historial ---
        registro_frame = QFrame()
        registro_frame.setStyleSheet("background-color: #1f2232; border-radius: 15px;")
        registro_layout = QVBoxLayout(registro_frame)

        subtitle = QLabel("Registro de datos")
        subtitle.setObjectName("Subtitle")

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setStyleSheet("""
            QHeaderView::section {
                background-color: #7FD1B9;
                color: black;
                padding: 5px;
                border: none;
                font-weight: bold;
            }
                                 
            QTableCornerButton::section {
                background-color: #1f2232;
                border: none;
            }
        """)
        self.table.setHorizontalHeaderLabels(["PH", "CE", "Temperatura en Agua", "Nivel del agua", "Temperatura en Ambiente", "Humedad", "Fecha"])
        self.table.horizontalHeader().setFixedHeight(25)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.populate_table()

        registro_layout.addWidget(subtitle)
        registro_layout.addWidget(self.table)

        historial_layout.addWidget(title_historial)
        historial_layout.addLayout(top_buttons_layout)
        historial_layout.addSpacing(10)
        historial_layout.addWidget(registro_frame)

        layout.addWidget(historial_frame)
    
    def populate_table(self):
        datos = [
            [6.5, 1.2, 22, 1.2, 10, 80, "2025-04-25"],
            [6.5, 1.2, 23, 1.3, 5, 78, "2025-04-24"],
            [6.5, 1.2, 21, 1.5, 15, 82, "2025-04-23"],
        ]

        self.table.setRowCount(len(datos))

        # Personalizar el encabezado vertical (para numeración automática)
        vertical_header = self.table.verticalHeader()
        vertical_header.setDefaultAlignment(Qt.AlignCenter)
        vertical_header.setStyleSheet("""
            QHeaderView::section {
                background-color: #7FD1B9;
                color: black;
                font-weight: bold;
                border: none;
            }
        """)

        bold_font = QFont()
        bold_font.setBold(True)

        for i, fila in enumerate(datos):
            for j, valor in enumerate(fila):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, j, item)








