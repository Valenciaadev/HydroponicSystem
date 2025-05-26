from PyQt5.QtWidgets import *
from models.database import (
    getAll,
    getbyMonth,
    getbyQuarter,
    getbySemester,
    getbyYear,
    get_averages_by_months,
    get_averages_by_weeks,
    get_averages_all,
    get_date_ranges,
)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import rcParams
import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QToolTip
from reportlab.lib.pagesizes import landscape, letter
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

class HistoryAppAdmin(QWidget):
    def __init__(self, ventana_login, embed=None):
        super().__init__(ventana_login)
        self.ventana_login = ventana_login
        self.current_filter = None
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
                padding: 5px;
                border-radius: 10px;
                background-color: #2E2E3A;
                color: white;
            }
            QTableWidget {
                gridline-color: #7FD1B9;
                color: white;
                border: none;
            }
        """)

        layout = QVBoxLayout(self)

        # --- Cuadro Historial ---
        historial_frame = QFrame()
        historial_frame.setStyleSheet("background-color: #27243A; border-radius: 10px;")
        historial_frame.setContentsMargins(20, 10, 20, 20)
        self.historial_layout = QVBoxLayout(historial_frame)

        # --- Layout para el título y los botones ---
        title_buttons_layout = QHBoxLayout()


        # Buscar ícono según el nombre
        icon_path = "assets/icons/history.svg"

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

        title_historial = QLabel("Historial")
        title_historial.setObjectName("Title")
        title_buttons_layout.addWidget(icon_label)
        title_buttons_layout.addWidget(title_historial, alignment=Qt.AlignVCenter)
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
        self.filter_combo.setCurrentText("Mes anterior")
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
        self.table.setHorizontalHeaderLabels(["PH", "ORP", "Temperatura en Agua", "Nivel del agua",
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

        
        self.populate_icons = {
            "Datos con gráficas": "assets/img/grafica.png",
            "Datos con tabla": "assets/img/tabla.png"
        }

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
            
                    # Buscar ícono según el nombre
            icon_path = self.populate_icons.get(nombre, "assets/img/logo.png")

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
                ax1.set_title('Variación de PH y ORP', color='white')
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


            device_layout.addWidget(icon_label)
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

    def mostrar_mensaje_error(self, mensaje):
        # Limpiar gráficas
        for ax in [self.ax1, self.ax2, self.ax3]:
            ax.clear()
            ax.text(0.5, 0.5, mensaje, 
                ha='center', va='center', color='white')
            ax.set_facecolor('#1f2232')
        
        self.canvas1.draw()
        self.canvas2.draw()
        self.canvas3.draw()
        
        # Opcional: Mostrar mensaje en un QMessageBox
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.warning(self, "Datos no disponibles", mensaje)

    def update_graphs(self, datos):
        """Actualiza las gráficas con los datos proporcionados"""
        if not datos:
            return
        
        filtro = self.filter_combo.currentText()

        # Configuración inicial de ejes Y para todas las gráficas
        self.ax1.clear()
        self.ax1.set_ylim(0, 9)
        self.ax1.set_yticks([0, 3, 6, 9])
        
        self.ax2.clear()
        self.ax2.set_ylim(0, 40)
        self.ax2.set_yticks([0, 20, 40])
        
        self.ax3.clear()
        self.ax3.set_ylim(0, 105)
        self.ax3.set_yticks([0, 35, 70, 105])
        
        try:
            if filtro == "Todo":
                # Obtener promedios generales
                promedios = get_averages_all()
                if promedios and all(p is not None for p in promedios):
                    avg_ph, avg_ce, avg_t_agua, avg_nivel, avg_t_ambiente, avg_humedad = promedios
                    
                    # Configuración común para gráficas de barras
                    bar_width = 0.35
                    index = np.arange(2)  # Dos grupos de barras
                    
                    # Gráfica 1 (PH y CE)
                    self.ax1.bar(index[0], avg_ph, bar_width, color='#60D4B8', label='PH')
                    self.ax1.bar(index[1], avg_ce, bar_width, color='#4A90E2', label='ORP')
                    self.ax1.set_title('Promedios de PH y ORP', color='white')
                    self.ax1.set_xticks(index)
                    self.ax1.set_xticklabels(['Sensor PH', 'Sensor ORP'], color='white')
                    self.ax1.legend()
                    
                    # Añadir etiquetas de valores
                    for i, val in enumerate([avg_ph, avg_ce]):
                        self.ax1.text(i, val, f"{val:.2f}", ha='center', va='bottom', color='white')
                    
                    # Gráfica 2 (Temperaturas)
                    self.ax2.bar(index[0], avg_t_agua, bar_width, color='#60D4B8', label='Temp Agua')
                    self.ax2.bar(index[1], avg_t_ambiente, bar_width, color='#4A90E2', label='Temp Ambiente')
                    self.ax2.set_title('Promedios de Temperaturas', color='white')
                    self.ax2.set_xticks(index)
                    self.ax2.set_xticklabels(['Temp Agua', 'Temp Ambiente'], color='white')
                    self.ax2.legend()
                    
                    # Añadir etiquetas de valores
                    for i, val in enumerate([avg_t_agua, avg_t_ambiente]):
                        self.ax2.text(i, val, f"{val:.2f}", ha='center', va='bottom', color='white')
                    
                    # Gráfica 3 (Humedad y Nivel)
                    self.ax3.bar(index[0], avg_humedad, bar_width, color='#60D4B8', label='Humedad')
                    self.ax3.bar(index[1], avg_nivel, bar_width, color='#4A90E2', label='Nivel Agua')
                    self.ax3.set_title('Promedios de Humedad y Nivel', color='white')
                    self.ax3.set_xticks(index)
                    self.ax3.set_xticklabels(['Humedad', 'Nivel Agua'], color='white')
                    self.ax3.legend()
                    
                    # Añadir etiquetas de valores
                    for i, val in enumerate([avg_humedad, avg_nivel]):
                        self.ax3.text(i, val, f"{val:.2f}", ha='center', va='bottom', color='white')
            
            elif filtro == "Mes anterior":
                semanas = get_averages_by_weeks()
                if semanas and len(semanas) > 0 and all(all(v is not None for v in s) for s in semanas):
                    semanas_nums = get_date_ranges(weeks=True)  # Formato "May 17 - Abr 21"
                    ph_values = [s[0] for s in semanas]
                    ce_values = [s[1] for s in semanas]
                    t_agua_values = [s[2] for s in semanas]
                    t_ambiente_values = [s[4] for s in semanas]
                    humedad_values = [s[5] for s in semanas]
                    nivel_values = [s[3] for s in semanas]
                    
                    # Gráfica 1 (PH y CE)
                    self.ax1.plot(semanas_nums, ph_values, 'o-', color='#60D4B8', label='PH')
                    self.ax1.plot(semanas_nums, ce_values, 'o-', color='#4A90E2', label='ORP')
                    self.ax1.set_title('Variación semanal de PH y ORP', color='white')
                    self.ax1.legend()
                    
                    # Añadir etiquetas de valores
                    for i, (ph, ce) in enumerate(zip(ph_values, ce_values)):
                        if ph is not None and ce is not None:
                            self.ax1.text(i, ph, f"{ph:.2f}", ha='center', va='bottom', color='white')
                            self.ax1.text(i, ce, f"{ce:.2f}", ha='center', va='bottom', color='white')
                    
                    # Gráfica 2 (Temperaturas)
                    self.ax2.plot(semanas_nums, t_agua_values, 'o-', color='#60D4B8', label='Temp Agua')
                    self.ax2.plot(semanas_nums, t_ambiente_values, 'o-', color='#4A90E2', label='Temp Ambiente')
                    self.ax2.set_title('Variación semanal de Temperaturas', color='white')
                    self.ax2.legend()
                    
                    # Añadir etiquetas de valores
                    for i, (tagua, tamb) in enumerate(zip(t_agua_values, t_ambiente_values)):
                        if tagua is not None and tamb is not None:
                            self.ax2.text(i, tagua, f"{tagua:.2f}", ha='center', va='bottom', color='white')
                            self.ax2.text(i, tamb, f"{tamb:.2f}", ha='center', va='bottom', color='white')
                    
                    # Gráfica 3 (Humedad y Nivel)
                    self.ax3.plot(semanas_nums, humedad_values, 'o-', color='#60D4B8', label='Humedad')
                    self.ax3.plot(semanas_nums, nivel_values, 'o-', color='#4A90E2', label='Nivel Agua')
                    self.ax3.set_title('Variación semanal de Humedad y Nivel', color='white')
                    self.ax3.legend()
                    
                    # Añadir etiquetas de valores
                    for i, (hum, niv) in enumerate(zip(humedad_values, nivel_values)):
                        if hum is not None and niv is not None:
                            self.ax3.text(i, hum, f"{hum:.2f}", ha='center', va='bottom', color='white')
                            self.ax3.text(i, niv, f"{niv:.2f}", ha='center', va='bottom', color='white')
            
            elif filtro in ["Último trimestre", "Último semestre", "Último año"]:
                months = 3 if filtro == "Último trimestre" else 6 if filtro == "Último semestre" else 12
                meses = get_averages_by_months(months)
                if meses and len(meses) > 0 and all(all(v is not None for v in m) for m in meses):
                    meses_nums = get_date_ranges(months=months)  # Formato "May - Abr"
                    ph_values = [s[0] for s in meses]
                    ce_values = [s[1] for s in meses]
                    t_agua_values = [s[2] for s in meses]
                    t_ambiente_values = [s[4] for s in meses]
                    humedad_values = [s[5] for s in meses]
                    nivel_values = [s[3] for s in meses]
                    
                    # Gráfica 1 (PH y CE)
                    self.ax1.plot(meses_nums, ph_values, 'o-', color='#60D4B8', label='PH')
                    self.ax1.plot(meses_nums, ce_values, 'o-', color='#4A90E2', label='ORP')
                    self.ax1.set_title(f'Variación mensual de PH y ORP ({filtro.lower()})', color='white')
                    self.ax1.legend()
                    
                    # Añadir etiquetas de valores
                    for i, (ph, ce) in enumerate(zip(ph_values, ce_values)):
                        if ph is not None and ce is not None:
                            self.ax1.text(i, ph, f"{ph:.2f}", ha='center', va='bottom', color='white')
                            self.ax1.text(i, ce, f"{ce:.2f}", ha='center', va='bottom', color='white')
                    
                    # Gráfica 2 (Temperaturas)
                    self.ax2.plot(meses_nums, t_agua_values, 'o-', color='#60D4B8', label='Temp Agua')
                    self.ax2.plot(meses_nums, t_ambiente_values, 'o-', color='#4A90E2', label='Temp Ambiente')
                    self.ax2.set_title(f'Variación mensual de Temperaturas ({filtro.lower()})', color='white')
                    self.ax2.legend()
                    
                    # Añadir etiquetas de valores
                    for i, (tagua, tamb) in enumerate(zip(t_agua_values, t_ambiente_values)):
                        if tagua is not None and tamb is not None:
                            self.ax2.text(i, tagua, f"{tagua:.2f}", ha='center', va='bottom', color='white')
                            self.ax2.text(i, tamb, f"{tamb:.2f}", ha='center', va='bottom', color='white')
                    
                    # Gráfica 3 (Humedad y Nivel)
                    self.ax3.plot(meses_nums, humedad_values, 'o-', color='#60D4B8', label='Humedad')
                    self.ax3.plot(meses_nums, nivel_values, 'o-', color='#4A90E2', label='Nivel Agua')
                    self.ax3.set_title(f'Variación mensual de Humedad y Nivel ({filtro.lower()})', color='white')
                    self.ax3.legend()
                    
                    # Añadir etiquetas de valores
                    for i, (hum, niv) in enumerate(zip(humedad_values, nivel_values)):
                        if hum is not None and niv is not None:
                            self.ax3.text(i, hum, f"{hum:.2f}", ha='center', va='bottom', color='white')
                            self.ax3.text(i, niv, f"{niv:.2f}", ha='center', va='bottom', color='white')
        
        except Exception as e:
            print(f"Error al actualizar gráficas: {e}")
            for ax in [self.ax1, self.ax2, self.ax3]:
                ax.text(0.5, 0.5, 'Datos no disponibles', 
                    ha='center', va='center', color='white')
                ax.set_facecolor('#1f2232')
        
        # Configuración común para todas las gráficas
        for ax in [self.ax1, self.ax2, self.ax3]:
            ax.grid(True, color='#444')
            ax.set_facecolor('#1f2232')
            ax.tick_params(axis='x', colors='white', rotation=0)  # Texto horizontal
            ax.tick_params(axis='y', colors='white')
        
        # Redibujar las gráficas
        self.canvas1.draw()
        self.canvas2.draw()
        self.canvas3.draw()

    def populate_table(self):
        filtro = self.filter_combo.currentText()
        
        # Solo actualizar si el filtro ha cambiado
        if hasattr(self, 'current_filter') and self.current_filter == filtro:
            return
            
        self.current_filter = filtro  # Guardar el filtro actual
        
        try:
            match filtro:
                case "Todo":
                    self.datos_completos = getAll() or []
                case "Mes anterior":
                    self.datos_completos = getbyMonth() or []
                case "Último trimestre":
                    self.datos_completos = getbyQuarter() or []
                case "Último semestre":
                    self.datos_completos = getbySemester() or []
                case "Último año":
                    self.datos_completos = getbyYear() or []
                case _:
                    self.datos_completos = []
        except Exception as e:
            print(f"Error al obtener datos: {e}")
            self.datos_completos = []

        self.pagina_actual = 0
        self.mostrar_pagina()
        
        # Solo actualizar gráficas si hay datos
        if self.datos_completos:
            self.update_graphs(self.datos_completos)
        else:
            self.mostrar_mensaje_error(f"No hay datos disponibles para el filtro: {filtro}")

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
        self.fig1.savefig(graph1_path, facecolor='#1f2232', bbox_inches='tight', dpi=150)
        self.fig2.savefig(graph2_path, facecolor='#1f2232', bbox_inches='tight', dpi=150)
        self.fig3.savefig(graph3_path, facecolor='#1f2232', bbox_inches='tight', dpi=150)

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
        c.setFont("Helvetica-Bold", 36)
        c.setFillColor(colors.black)
        c.drawString(160, height - 100, "HydroBox")
        c.setFont("Helvetica", 12)
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
        headers = ["PH", "ORP", "Temp. Agua", "Nivel Agua", "Temp. Ambiente", "Humedad", "Fecha y Hora"]
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