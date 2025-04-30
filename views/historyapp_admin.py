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
from models.database import (
    getAll,
    getbyMonth,
    getbyQuarter,
    getbySemester,
    getbyYear,
)
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PyQt5.QtWidgets import QFileDialog
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
        self.pdf_button.setIcon(QIcon("assets/icons/bxs-file-pdf.svg")) 
        self.pdf_button.setFixedSize(50, 50)  
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

        self.filter_combo.currentIndexChanged.connect(self.populate_table)

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
        self.table.setHorizontalHeaderLabels(["PH", "CE", "Temperatura en Agua", "Nivel del agua", "Temperatura en Ambiente", "Humedad", "Fecha y Hora"])
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

        self.pdf_button.clicked.connect(self.generate_pdf)
    
    def populate_table(self):
        """Llena la tabla con datos según el filtro seleccionado."""
        filtro = self.filter_combo.currentText()
        
        match filtro:
            case "Todo":
                datos = getAll()
            case "Mes anterior":
                datos = getbyMonth()
            case "Último trimestre":
                datos = getbyQuarter()
            case "Último semestre":
                datos = getbySemester()
            case "Último año":
                datos = getbyYear()
            case _:
                datos = []

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

        for i, fila in enumerate(datos):
            for j, valor in enumerate(fila):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, j, item)
            
    def generate_pdf(self):
        """Genera un PDF con los datos visibles en la tabla."""
        # Abrir un cuadro de diálogo para guardar el archivo
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Guardar PDF", "", "Archivos PDF (*.pdf)", options=options
        )

        if not file_path:
            return  # Si el usuario cancela, no hacer nada

        # Crear el PDF
        c = canvas.Canvas(file_path, pagesize=letter)
        width, height = letter

        # Título del PDF
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "Historial de Mediciones")

        # Subtítulo con el filtro seleccionado
        filtro = self.filter_combo.currentText()
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 80, f"Filtro aplicado: {filtro}")

        # Encabezados de la tabla
        headers = ["PH", "CE", "Temp. Agua", "Nivel Agua", "Temp. Ambiente", "Humedad", "Fecha y Hora"]
        x_offset = 50
        y_offset = height - 120
        c.setFont("Helvetica-Bold", 10)
        for i, header in enumerate(headers):
            c.drawString(x_offset + i * 80, y_offset, header)

        # Dibujar los datos de la tabla
        c.setFont("Helvetica", 10)
        y_offset -= 20
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item is not None:
                    c.drawString(x_offset + col * 80, y_offset, item.text())
            y_offset -= 20
            if y_offset < 50:  # Crear una nueva página si no hay espacio
                c.showPage()
                y_offset = height - 50

        # Guardar el PDF
        c.save()

        # Confirmación
        print(f"PDF guardado en: {file_path}")








