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
    QVBoxLayout, QHBoxLayout, QFrame, QHeaderView, QFileDialog
)
from models.database import (
    getAll,
    getbyMonth,
    getbyQuarter,
    getbySemester,
    getbyYear,
)
from reportlab.lib.pagesizes import ( landscape, letter
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QIcon, QColor, QFont
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas


class HistoryAppAdmin(QWidget):
    def __init__(self, ventana_login, embed=None):
        super().__init__(ventana_login)
        self.ventana_login = ventana_login
        self.init_ui()



    def init_ui(self):
        self.datos_completos = []
        self.pagina_actual = 0
        self.registros_por_pagina = 15
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
        historial_frame.setStyleSheet("background-color: #27243A; border-radius: 15px; padding: 15px")
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
        registro_frame.setStyleSheet("background-color: #1f2232; border-radius: 15px; ")
        registro_layout = QVBoxLayout(registro_frame)
        registro_layout.setSpacing(5)


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


        registro_layout.addWidget(subtitle)
        registro_layout.addWidget(self.table)

        self.paginacion_layout = QHBoxLayout()
        self.paginacion_layout.setAlignment(Qt.AlignCenter)

        self.boton_anterior = QPushButton("← Anterior")
        self.boton_siguiente = QPushButton("Siguiente →")
        self.boton_anterior.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                padding: 8px 16px;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
        """)

        self.boton_siguiente.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                padding: 8px 16px;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
        """)

        self.boton_anterior.clicked.connect(self.ir_pagina_anterior)
        self.boton_siguiente.clicked.connect(self.ir_pagina_siguiente)

        self.paginacion_layout.addWidget(self.boton_anterior)
        self.paginacion_layout.addWidget(self.boton_siguiente)

        registro_layout.addLayout(self.paginacion_layout)
        self.populate_table()


        historial_layout.addWidget(title_historial)
        historial_layout.addLayout(top_buttons_layout)
        historial_layout.addSpacing(10)
        historial_layout.addWidget(registro_frame)

        layout.addWidget(historial_frame)

        self.pdf_button.clicked.connect(self.generate_pdf)
    
    def populate_table(self):
        filtro = self.filter_combo.currentText()

        match filtro:
            case "Todo":
                self.datos_completos = getAll()
            case "Mes anterior":
                self.datos_completos = getbyMonth()
            case "Último trimestre":
                self.datos_completos = getbyQuarter()
            case "Último semestre":
                self.datos_completos = getbySemester()
            case "Último año":
                self.datos_completos = getbyYear()
            case _:
                self.datos_completos = []

        self.pagina_actual = 0
        self.mostrar_pagina()

    def mostrar_pagina(self):
        inicio = self.pagina_actual * self.registros_por_pagina
        fin = inicio + self.registros_por_pagina
        pagina_datos = self.datos_completos[inicio:fin]

        self.table.setRowCount(len(pagina_datos))

        for i, fila in enumerate(pagina_datos):
            for j, valor in enumerate(fila):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, j, item)

        # Mostrar/ocultar botones
        total_paginas = (len(self.datos_completos) - 1) // self.registros_por_pagina
        self.boton_anterior.setVisible(self.pagina_actual > 0)
        self.boton_siguiente.setVisible(self.pagina_actual < total_paginas)

    def ir_pagina_siguiente(self):
        self.pagina_actual += 1
        self.mostrar_pagina()

    def ir_pagina_anterior(self):
        self.pagina_actual -= 1
        self.mostrar_pagina()

            
    def generate_pdf(self):
        """Genera un PDF con todos los datos del filtro seleccionado, no solo los visibles en la tabla."""
        # Diálogo para guardar
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Guardar PDF", "", "Archivos PDF (*.pdf)", options=options
        )

        if not file_path:
            return

        c = canvas.Canvas(file_path, pagesize=landscape(letter))
        width, height = landscape(letter)

        filtro = self.filter_combo.currentText()

        # Encabezado de la tabla
        headers = ["PH", "CE", "Temp. Agua", "Nivel Agua", "Temp. Ambiente", "Humedad", "Fecha y Hora"]
        data = [headers] + self.datos_completos  # Usar todos los datos del filtro seleccionado

        # Estilo de la tabla
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4A90E2")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F5F5F5")),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])

        # Parámetros de paginación
        margin_top = 100
        margin_bottom = 50
        available_height = height - margin_top - margin_bottom
        row_height = 20  # Altura aproximada de cada fila

        max_rows_per_page = int(available_height // row_height) - 1  # -1 para el encabezado

        current_row = 1  # Saltamos encabezado porque ya está en data[0]
        total_rows = len(data) - 1

        def draw_header():
            """Dibuja el encabezado en la página actual."""
            c.setFont("Helvetica-Bold", 20)
            c.drawCentredString(width / 2, height - 40, "Historial de Mediciones")
            c.setFont("Helvetica", 14)
            c.drawCentredString(width / 2, height - 65, f"Filtro aplicado: {filtro}")

        while current_row <= total_rows:
            if current_row == 1:  # Solo dibujar el encabezado en la primera página
                draw_header()

            # Obtener los datos para la página actual
            page_data = [headers] + data[current_row: current_row + max_rows_per_page]
            colWidths = [80, 80, 80, 80, 110, 80, 160]
            table = Table(page_data, colWidths=colWidths)
            table.setStyle(table_style)

            table_width, table_height = table.wrap(0, 0)
            x_position = (width - table_width) / 2
            y_position = height - margin_top - table_height

            table.drawOn(c, x_position, y_position)

            current_row += max_rows_per_page

            if current_row <= total_rows:  # Si hay más datos, crear una nueva página
                c.showPage()
                # En las páginas siguientes, no dibujar el encabezado
                y_position = height - margin_top

        c.save()
        print(f"PDF guardado en: {file_path}")