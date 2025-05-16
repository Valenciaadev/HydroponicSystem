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
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import rcParams
import numpy as np
from PyQt5.QtCore import QPoint, QRect
from PyQt5.QtWidgets import QToolTip
from reportlab.lib.pagesizes import landscape, letter
from PyQt5.QtCore import Qt, QSize
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
        icon = QIcon("assets/icons/bxs-file-pdf.svg")
        pixmap = icon.pixmap(QSize(34, 34)) # Obtener un QPixmap escalado del QIcon
        self.pdf_button.setIcon(QIcon(pixmap)) # Establecer el QIcon creado a partir del QPixmap escalado
        self.pdf_button.setFixedSize(46, 46)
        self.pdf_button.setIconSize(QSize(46, 46))
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
        self.arrow_buttons = {}  # Diccionario para guardar los botones de flecha
        self.content_frames = {} # Diccionario para guardar los frames de contenido

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
            self.arrow_buttons[nombre] = arrow_button # Guardar referencia al botón

            # Configurar el frame de contenido
            if nombre == "Datos con gráficas":
                content_frame = QFrame()
                content_frame.setObjectName("graphics_content")
                content_frame.setStyleSheet("background-color: #1f2232; border-radius: 15px;")
                content_frame.setFixedHeight(750)
                content_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                content_layout = QVBoxLayout(content_frame)
                
                # --- Crear header con título y botón de info ---
                header_widget = QWidget()
                header_layout = QHBoxLayout(header_widget)
                header_layout.setContentsMargins(0, 0, 0, 0)
                
                """ title_label = QLabel("Visualización de Datos")
                title_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;") """
                
                # Botón de información
                info_button = QPushButton()
                Icon_i = QIcon("assets/icons/info-circle.svg")
                pixmap = Icon_i.pixmap(QSize(28, 28))
                info_button.setIcon(QIcon(pixmap))
                info_button.setFixedSize(46,46)
                info_button.setIconSize(QSize(46, 46))
                info_button.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border: none;
                        margin-right: 15px;
                        margin-top: 15px;
                    }
                    QPushButton:hover {
                        background-color: #444;
                        border-radius: 15px;
                    }
                """)

                # Definir una clase personalizada para manejar el evento hover
                class InfoButtonEnterEvent:
                    def __init__(self, button):
                        self.button = button
                        
                    def enterEvent(self, event):
                        QToolTip.showText(
                            self.button.mapToGlobal(QPoint(0, 20)),  # Posición arriba del botón
                            """
                            <span style='font-size: 12pt; color: white;'>
                            <b>Información sobre las gráficas:</b><br><br>
                            Los valores mostrados en las gráficas están promediados<br>
                            según el filtro de tiempo seleccionado:<br><br>
                            • <b>Todo:</b> Promedio general<br>
                            • <b>Mes anterior:</b> Promedio del último mes<br>
                            • <b>Último trimestre:</b> Promedio de los últimos 3 meses<br>
                            • <b>Último semestre:</b> Promedio de los últimos 6 meses<br>
                            • <b>Último año:</b> Promedio de los últimos 12 meses<br>
                            </span>
                            """,
                            self.button,
                            QRect(),  # Área de activación
                            0  # Tiempo visible (0 = hasta que el mouse se mueva)
                        )
                        super(type(self.button), self.button).enterEvent(event)

                # Aplicar el evento personalizado al botón
                info_button.enterEvent = InfoButtonEnterEvent(info_button).enterEvent

                header_layout.addStretch()
                header_layout.addWidget(info_button)
                
                # --- Contenedor de gráficas ---
                graphics_container = QWidget()
                graphics_container.setStyleSheet("background-color: #1f2232;")
                graphics_layout = QVBoxLayout(graphics_container)
                
                # Configurar estilo de matplotlib
                rcParams['axes.facecolor'] = '#1f2232'
                rcParams['axes.edgecolor'] = 'white'
                rcParams['axes.labelcolor'] = 'white'
                rcParams['xtick.color'] = 'white'
                rcParams['ytick.color'] = 'white'
                rcParams['text.color'] = 'white'
                
                # Gráfica 1: PH y CE
                fig1 = Figure(figsize=(10, 4), facecolor='#1f2232')
                canvas1 = FigureCanvas(fig1)
                ax1 = fig1.add_subplot(111)
                ax1.set_title('Variación de PH y CE', color='white')
                ax1.set_xlabel('Muestras')
                ax1.set_ylabel('Valores')
                ax1.grid(True, color='#444')
                
                # Gráfica 2: Temperaturas
                fig2 = Figure(figsize=(10, 4), facecolor='#1f2232')
                canvas2 = FigureCanvas(fig2)
                ax2 = fig2.add_subplot(111)
                ax2.set_title('Temperaturas (Agua y Ambiente)', color='white')
                ax2.set_xlabel('Muestras')
                ax2.set_ylabel('°C')
                ax2.grid(True, color='#444')
                
                # Gráfica 3: Humedad y Nivel de agua
                fig3 = Figure(figsize=(10, 4), facecolor='#1f2232')
                canvas3 = FigureCanvas(fig3)
                ax3 = fig3.add_subplot(111)
                ax3.set_title('Humedad y Nivel de agua', color='white')
                ax3.set_xlabel('Muestras')
                ax3.set_ylabel('Valores')
                ax3.grid(True, color='#444')
                
                # Añadir las gráficas al layout
                graphics_layout.addWidget(canvas1)
                graphics_layout.addWidget(canvas2)
                graphics_layout.addWidget(canvas3)
                
                # Añadir el contenedor al layout principal
                content_layout.addWidget(header_widget)
                content_layout.addWidget(graphics_container)
                
                self.content_frames[nombre] = content_frame
                arrow_button.clicked.connect(lambda checked, f=content_frame, b=arrow_button, n=nombre:
                                            self.toggle_content_frame(f, b, n))
                self.devices_list_layout.addWidget(outer_frame)
                self.devices_list_layout.addWidget(content_frame)
                content_frame.hide()
                
                # Guardar referencias para actualizar datos
                self.fig1 = fig1
                self.ax1 = ax1
                self.canvas1 = canvas1
                self.fig2 = fig2
                self.ax2 = ax2
                self.canvas2 = canvas2
                self.fig3 = fig3
                self.ax3 = ax3
                self.canvas3 = canvas3
            else: # nombre == "Datos con tabla"
                table_content_frame = QFrame()
                table_content_frame.setObjectName("table_content")
                table_content_frame.setStyleSheet("background-color: #1f2232; border-radius: 15px;")
                table_content_frame.setFixedHeight(750)
                table_content_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                table_content_layout = QVBoxLayout(table_content_frame)
                table_content_layout.addWidget(self.registro_frame)
                self.content_frames[nombre] = table_content_frame
                arrow_button.clicked.connect(lambda checked, f=table_content_frame, b=arrow_button, n=nombre:
                                        self.toggle_content_frame(f, b, n))
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

    def toggle_content_frame(self, current_frame, current_button, current_name):
        """Alterna la visibilidad del frame de contenido, cerrando el otro si está abierto"""
        # Si el frame actual está visible, lo ocultamos
        if current_frame.isVisible():
            current_frame.hide()
            current_button.setIcon(QIcon("assets/icons/bxs-down-arrow.svg"))
        else:
            # Primero cerramos cualquier otro frame que esté abierto
            for name, frame in self.content_frames.items():
                if name != current_name and frame.isVisible():
                    frame.hide()
                    self.arrow_buttons[name].setIcon(QIcon("assets/icons/bxs-down-arrow.svg"))
            
            # Luego mostramos el frame actual
            current_frame.show()
            current_button.setIcon(QIcon("assets/icons/bxs-up-arrow.svg"))

    def update_graphs(self, datos):
        """Actualiza las gráficas con los datos proporcionados"""
        if not datos:
            return
        
        # Extraer datos para las gráficas
        ph = [d[0] for d in datos]
        ce = [d[1] for d in datos]
        temp_agua = [d[2] for d in datos]
        nivel_agua = [d[3] for d in datos]
        temp_ambiente = [d[4] for d in datos]
        humedad = [d[5] for d in datos]
        fechas = [d[6] for d in datos]
        
        # Limpiar gráficas anteriores
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        
        # Configurar gráfica 1 (PH y CE)
        self.ax1.plot(ph, label='PH', color='#60D4B8')
        self.ax1.plot(ce, label='CE', color='#4A90E2')
        self.ax1.set_title('Variación de PH y CE', color='white')
        self.ax1.set_xlabel('Muestras')
        self.ax1.set_ylabel('Valores')
        self.ax1.legend()
        self.ax1.grid(True, color='#444')
        
        # Configurar gráfica 2 (Temperaturas)
        self.ax2.plot(temp_agua, label='Temperatura agua', color='#60D4B8')
        self.ax2.plot(temp_ambiente, label='Temperatura ambiente', color='#4A90E2')
        self.ax2.set_title('Temperaturas (Agua y Ambiente)', color='white')
        self.ax2.set_xlabel('Muestras')
        self.ax2.set_ylabel('°C')
        self.ax2.legend()
        self.ax2.grid(True, color='#444')
        
        # Configurar gráfica 3 (Humedad y Nivel de agua)
        self.ax3.plot(humedad, label='Humedad', color='#60D4B8')
        self.ax3.plot(nivel_agua, label='Nivel agua', color='#4A90E2')
        self.ax3.set_title('Humedad y Nivel de agua', color='white')
        self.ax3.set_xlabel('Muestras')
        self.ax3.set_ylabel('Valores')
        self.ax3.legend()
        self.ax3.grid(True, color='#444')
        
        # Redibujar las gráficas
        self.canvas1.draw()
        self.canvas2.draw()
        self.canvas3.draw()

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
        self.update_graphs(self.datos_completos)  # Actualizar gráficas con los nuevos datos

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
        """Genera un PDF con gráficas y datos del filtro seleccionado"""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Guardar PDF", "", "Archivos PDF (*.pdf)", options=options
        )

        if not file_path:
            return

        # Crear imágenes temporales de las gráficas
        import tempfile
        temp_dir = tempfile.mkdtemp()
        graph1_path = f"{temp_dir}/graph1.png"
        graph2_path = f"{temp_dir}/graph2.png"
        graph3_path = f"{temp_dir}/graph3.png"
        
        # Guardar las gráficas con fondo transparente
        self.fig1.savefig(graph1_path, transparent=True, bbox_inches='tight', dpi=150)
        self.fig2.savefig(graph2_path, transparent=True, bbox_inches='tight', dpi=150)
        self.fig3.savefig(graph3_path, transparent=True, bbox_inches='tight', dpi=150)

        # Crear el PDF
        c = canvas.Canvas(file_path, pagesize=landscape(letter))
        width, height = landscape(letter)
        filtro = self.filter_combo.currentText()

        # --- PRIMERA PÁGINA (GRÁFICAS) ---
        # Fondo blanco para toda la página
        c.setFillColor(colors.white)
        c.rect(0, 0, width, height, fill=True, stroke=False)
        
        # Logo con transparencia
        logo_path = "assets/img/logo.png"
        c.drawImage(logo_path, 50, height - 140, width=100, height=100, 
                preserveAspectRatio=True, mask='auto')
        
        # Texto HydroBox y filtro
        c.setFont("Helvetica-Bold", 28)
        c.setFillColor(colors.black)
        c.drawString(160, height - 100, "HydroBox")
        c.setFont("Helvetica", 16)
        c.drawString(160, height - 130, f"Filtro aplicado: {filtro}")
        
        # Ajustar posición de las gráficas más abajo (inicio en height - 300)
        graph_height = (height - 350) / 2  # Altura para cada gráfica
        
        # Dos gráficas en la fila superior
        c.drawImage(graph1_path, 50, height - 300, 
                width=(width-150)/2, height=graph_height, 
                preserveAspectRatio=True, mask='auto')
        c.drawImage(graph2_path, (width-150)/2 + 100, height - 300, 
                width=(width-150)/2, height=graph_height, 
                preserveAspectRatio=True, mask='auto')
        
        # Una gráfica en la fila inferior (más ancha)
        c.drawImage(graph3_path, 50, height - 300 - graph_height - 30, 
                width=width-100, height=graph_height, 
                preserveAspectRatio=True, mask='auto')
        
        # Pie de página
        footer_text = "© 2025 HydroBox. Proyecto académico realizado para fines educativos. Todos los derechos reservados."
        c.setFont("Helvetica", 10)
        c.drawCentredString(width/2, 40, footer_text)
        
        c.showPage()  # Terminar la primera página
        
        # --- SEGUNDA PÁGINA EN ADELANTE (DATOS EN TABLA) ---
        headers = ["PH", "CE", "Temp. Agua", "Nivel Agua", "Temp. Ambiente", "Humedad", "Fecha y Hora"]
        data = [headers] + self.datos_completos

        # Configurar estilo de tabla mejorado
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#7FD1B9")),  # Verde más brillante
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),  # Fondo blanco
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#1f2232")),  # Bordes oscuros
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ])

        margin_top = 80
        margin_bottom = 50
        available_height = height - margin_top - margin_bottom
        row_height = 20
        max_rows_per_page = int(available_height // row_height) - 1

        current_row = 1
        total_rows = len(data) - 1

        while current_row <= total_rows:
            # Fondo blanco para la página
            c.setFillColor(colors.white)
            c.rect(0, 0, width, height, fill=True, stroke=False)
            
            # Pie de página
            c.setFont("Helvetica", 10)
            c.setFillColor(colors.black)
            c.drawCentredString(width/2, 40, footer_text)

            page_data = [headers] + data[current_row: current_row + max_rows_per_page]
            colWidths = [80, 80, 90, 80, 110, 80, 160]
            table = Table(page_data, colWidths=colWidths)
            table.setStyle(table_style)

            table_width, table_height = table.wrap(0, 0)
            x_position = (width - table_width) / 2
            y_position = height - margin_top - table_height

            table.drawOn(c, x_position, y_position)

            current_row += max_rows_per_page

            if current_row <= total_rows:
                c.showPage()

        c.save()
        print(f"PDF guardado en: {file_path}")
        
        # Limpiar archivos temporales
        import os
        os.remove(graph1_path)
        os.remove(graph2_path)
        os.remove(graph3_path)
        os.rmdir(temp_dir)