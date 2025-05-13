from PyQt5.QtWidgets import (
    QAbstractItemView, QWidget, QLabel, QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QHBoxLayout, QFrame, QHeaderView, QFileDialog, QSizePolicy
)
from models.database import (
    getAll,
    getbyMonth,
    getbyQuarter,
    getbySemester,
    getbyYear,
)
from reportlab.lib.pagesizes import landscape, letter
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
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
                font-size: 32px;
                font-weight: bold;
                color: white;
                margin-left: 30px;
                margin-top: 20px;
                margin-bottom: 20px;
            }
            QLabel#Subtitle {
                font-size: 22px;
                font-weight: bold;
                color: white;
                margin-top: 10px;
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
        historial_frame.setStyleSheet("background-color: #27243A; border-radius: 10px;")
        self.historial_layout = QVBoxLayout(historial_frame)

        # --- Layout para el título y los botones ---
        title_buttons_layout = QHBoxLayout()

        title_historial = QLabel("Historial")
        title_historial.setObjectName("Title")
        title_buttons_layout.addWidget(title_historial)
        title_buttons_layout.addStretch(1) # Empuja los widgets siguientes a la derecha

        top_buttons_layout = QHBoxLayout()

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
                border: 4px solid #60D4B8;
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

        title_buttons_layout.addLayout(top_buttons_layout) # Añadir el layout de botones al layout título-botones

        self.filter_combo.currentIndexChanged.connect(self.populate_table)

        # --- Lista de dispositivos ---
        self.devices_list_layout = QVBoxLayout()
        self.devices_list_layout.setSpacing(15)

        # --- Cuadro Tabla ---
        self.create_table_frame()

        self.historial_layout.addLayout(title_buttons_layout) # Añadir el layout combinado al historial_layout
        self.historial_layout.addLayout(self.devices_list_layout)
        self.historial_layout.addStretch(1)

        layout.addWidget(historial_frame)

        self.pdf_button.clicked.connect(self.generate_pdf)
        self.populate_devices()
        self.populate_table()

    def create_table_frame(self):
        """Crea el frame de la tabla que se usará para 'Datos con tabla'"""
        self.registro_frame = QFrame()
        self.registro_frame.setStyleSheet("background-color: #1f2232; border-radius: 15px;")
        registro_layout = QVBoxLayout(self.registro_frame)
        registro_layout.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Registro de datos")
        subtitle.setObjectName("Subtitle")

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setStyleSheet("""
            QHeaderView::section {
                background: #60D4B8;
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
        self.table.setHorizontalHeaderLabels(["PH", "CE", "Temperatura en Agua", "Nivel del agua",
                                            "Temperatura en Ambiente", "Humedad", "Fecha y Hora"])
        self.table.horizontalHeader().setFixedHeight(35)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setFixedSize(1450, 620)

        registro_layout.addWidget(subtitle, alignment=Qt.AlignCenter)
        registro_layout.addSpacing(20)
        registro_layout.addWidget(self.table, alignment=Qt.AlignCenter)

        self.paginacion_layout = QHBoxLayout()
        self.paginacion_layout.setAlignment(Qt.AlignCenter)

        self.boton_anterior = QPushButton("← Anterior")
        self.boton_siguiente = QPushButton("Siguiente →")
        self.boton_anterior.setStyleSheet("""
            QPushButton {
                background-color: #27243A;
                color: white;
                padding: 8px 16px;
                border-radius: 10px;
                border: 4px solid #60D4B8;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
        """)

        self.boton_siguiente.setStyleSheet("""
            QPushButton {
                background-color: #27243A;
                color: white;
                padding: 8px 16px;
                border-radius: 10px;
                border: 4px solid #60D4B8;
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

    def populate_devices(self):
        dispositivos = ["Datos con gráficas", "Datos con tabla"]

        for nombre in dispositivos:
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
            device_frame = QFrame()
            device_frame.setStyleSheet("""
                background-color: #1f2232;
                border-radius: 35px;
            """)
            device_frame.setFixedHeight(70)
            device_layout = QHBoxLayout(device_frame)
            device_layout.setContentsMargins(20, 10, 20, 10)

            name_label = QLabel(nombre)
            name_label.setStyleSheet("color: white; font-weight: bold; font-size: 16px;")

            # Botón de flecha
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

            # Configurar el frame de contenido
            if nombre == "Datos con gráficas":
                content_frame = QFrame()
                content_frame.setStyleSheet("background-color: #1f2232; border-radius: 15px;")
                content_frame.setFixedHeight(750)
                content_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                content_layout = QVBoxLayout(content_frame)
                content_layout.addWidget(QLabel("Aquí irán las gráficas"))

                arrow_button.clicked.connect(lambda checked, f=content_frame, b=arrow_button:
                                           self.toggle_content_frame(f, b))

                self.devices_list_layout.addWidget(outer_frame)
                self.devices_list_layout.addWidget(content_frame)
                content_frame.hide()
            else:
                # Para "Datos con tabla", crear un frame contenedor
                table_content_frame = QFrame()
                table_content_frame.setStyleSheet("background-color: #1f2232; border-radius: 15px;")
                table_content_frame.setFixedHeight(750)
                table_content_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                table_content_layout = QVBoxLayout(table_content_frame)

                # Añadir el registro_frame dentro de este frame
                table_content_layout.addWidget(self.registro_frame)

                arrow_button.clicked.connect(lambda checked, f=table_content_frame, b=arrow_button:
                                           self.toggle_content_frame(f, b))

                self.devices_list_layout.addWidget(outer_frame)
                self.devices_list_layout.addWidget(table_content_frame)
                table_content_frame.hide()

            buttons_layout = QHBoxLayout()
            buttons_layout.setSpacing(10)
            buttons_layout.addWidget(arrow_button)

            device_layout.addWidget(name_label)
            device_layout.addStretch()
            device_layout.addLayout(buttons_layout)

            # Asignar el interior al exterior
            outer_layout = QVBoxLayout(outer_frame)
            outer_layout.setContentsMargins(0, 0, 0, 0)
            outer_layout.addWidget(device_frame)

    def toggle_content_frame(self, frame, button):
        """Alterna la visibilidad del frame de contenido y cambia el icono del botón."""
        if frame.isVisible():
            frame.hide()
            button.setIcon(QIcon("assets/icons/bxs-down-arrow.svg"))
        else:
            frame.show()
            button.setIcon(QIcon("assets/icons/bxs-up-arrow.svg"))

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
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Guardar PDF", "", "Archivos PDF (*.pdf)", options=options
        )

        if not file_path:
            return

        c = canvas.Canvas(file_path, pagesize=landscape(letter))
        width, height = landscape(letter)

        filtro = self.filter_combo.currentText()

        headers = ["PH", "CE", "Temp. Agua", "Nivel Agua", "Temp. Ambiente", "Humedad", "Fecha y Hora"]
        data = [headers] + self.datos_completos

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

        margin_top = 100
        margin_bottom = 50
        available_height = height - margin_top - margin_bottom
        row_height = 20
        max_rows_per_page = int(available_height // row_height) - 1

        current_row = 1
        total_rows = len(data) - 1

        def draw_header():
            c.setFont("Helvetica-Bold", 20)
            c.drawCentredString(width / 2, height - 40, "Historial de Mediciones")
            c.setFont("Helvetica", 14)
            c.drawCentredString(width / 2, height - 65, f"Filtro aplicado: {filtro}")

        while current_row <= total_rows:
            if current_row == 1:
                draw_header()

            page_data = [headers] + data[current_row: current_row + max_rows_per_page]
            colWidths = [80, 80, 80, 80, 110, 80, 160]
            table = Table(page_data, colWidths=colWidths)
            table.setStyle(table_style)

            table_width, table_height = table.wrap(0, 0)
            x_position = (width - table_width) / 2
            y_position = height - margin_top - table_height

            table.drawOn(c, x_position, y_position)

            current_row += max_rows_per_page

            if current_row <= total_rows:
                c.showPage()
                y_position = height - margin_top

        c.save()
        print(f"PDF guardado en: {file_path}")