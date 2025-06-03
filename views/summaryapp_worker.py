from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from models.database import create_line_graph
from models.database import create_bar_graph
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from picamera2 import Picamera2
from PyQt5.QtCore import QTimer
import cv2
from PyQt5.QtGui import QImage, QPixmap
import matplotlib.pyplot as plt
import random
import math

class SummaryAppWorker(QWidget):
    def __init__(self, ventana_login, embed=False):
        super().__init__()
        self.gauges = {}
        self.sensor_data = {}  # Para conservar los últimos valores conocidos
        self.camera = None

        QToolTip.setFont(QFont("Arial", 12))
        QApplication.instance().setStyleSheet("""
            QToolTip {
                font-size: 12pt;
                color: white;
                background-color: #1E1B2E;
                border: 1px solid white;
                padding: 4px;
                border-radius: 6px;
                min-width: 300px;
                text-justify: auto;
            }
        """)

        # Este es el nuevo contenedor
        main_frame = QFrame()
        main_frame.setStyleSheet("background-color: #27243A; border-radius: 10px;")
        main_layout = QVBoxLayout(main_frame)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # ⬅️ Layout externo que contiene al frame
        outer_layout = QVBoxLayout()
        outer_layout.addWidget(main_frame)
        self.setLayout(outer_layout)

        layout = main_layout  # Seguimos usando el mismo nombre para no romper el resto del código

        # 1. Tarjetas superiores
        top_cards_layout = QHBoxLayout()
        top_cards_layout.setSpacing(20)
        
        cards_info = [
            (
                "Temperatura del aire", "0°", "00/0 00:00:00",
                "<b>Temperatura del Aire</b><br>"
                "Ideal entre <b>18°C y 24°C</b> para el crecimiento óptimo de lechugas.<br>"
                "Evita temperaturas mayores a 27°C para prevenir estrés térmico."
            ),
            (
                "Humedad del aire", "00.0", "00/0 00:00:00",
                "<b>Humedad Relativa del Aire</b><br>"
                "Rango ideal: <b>50% a 70%</b>.<br>"
                "Niveles adecuados reducen la transpiración excesiva y promueven la fotosíntesis."
            ),
            (
                "Temperatura del agua", "00°", "00/0 00:00:00",
                "<b>Temperatura del Agua</b><br>"
                "Ideal entre <b>18°C y 22°C</b>.<br>"
                "Temperaturas superiores a 24°C pueden reducir el oxígeno disuelto, afectando las raíces."
            ),
            (
                "Nivel pH del agua", "0 pH", "00/0 00:00:00",
                "<b>Nivel de pH del Agua</b><br>"
                "Rango óptimo: <b>5.5 a 6.5</b> para lechugas.<br>"
                "Valores fuera de este rango dificultan la absorción de nutrientes."
            ),
            (
                "Nivel ORP", "320 mV", "00/0 00:00:00",
                "<b>Potencial Redox (ORP)</b><br>"
                "Rango ideal para lechugas: <b>250 mV a 400 mV</b>.<br>"
                "Un ORP dentro de este rango indica un buen equilibrio entre oxidantes y reductores, "
                "lo cual favorece la absorción de nutrientes y evita la proliferación de microorganismos indeseados."
            ),
            (
                "Nivel del agua", "0 bool", "00/0 00:00:00",
                "<b>Nivel del Agua</b><br>"
                "Debe cubrir completamente las raíces sin llegar al tallo.<br>"
                "Se recomienda mantener un nivel constante para evitar estrés hídrico."
            ),
        ]


        for title, value, timestamp, tooltip in cards_info:
            card = self.create_card(title, value, timestamp, tooltip)
            top_cards_layout.addWidget(card)
        layout.addLayout(top_cards_layout)

        # 2. Segunda sección: 3 gauges verticales + gráfica + vista cámara
        middle_layout = QHBoxLayout()

        # 2.1 Gauges izquierdos
        middle_layout.addLayout(self.create_gauge_column(["PH Agua", "Temp. Agua", "ORP"]))

        # 2.2 INICIO DE LA GRÁFICA DE BARRAS //////////////////////
        self.graph_canvas_top = create_bar_graph()
        self.graph_canvas_top.setFixedSize(900, 400)

        graph_frame = QFrame()
        graph_frame.setStyleSheet("""
            background-color: #1f2232;
            border-radius: 20px;
            border: 2px solid #444444;
        """)
        graph_frame.setFixedSize(900, 400)

        graph_layout = QVBoxLayout(graph_frame)
        graph_layout.setContentsMargins(0, 0, 0, 0)
        graph_layout.addWidget(self.graph_canvas_top)

        middle_layout.addWidget(graph_frame)
        # FIN DE LA GRÁFICA DE BARRAS ////////////////////// 

        # 2.3 RECUADRO PARA LA CÁMARA //////////////////////
        camera_frame = QFrame()
        camera_frame.setFixedSize(405, 405)
        camera_frame.setStyleSheet("""
            background-color: #1f2232;
            border: 2px solid #444444;
            border-radius: 20px;
        """)
        camera_layout = QVBoxLayout(camera_frame)
        camera_layout.setContentsMargins(0, 0, 0, 0)

        self.camera_label = QLabel("Cargando cámara...")
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setStyleSheet("color: white; background-color: black;")
        self.camera_label.setFixedSize(400, 400)
        camera_layout.addWidget(self.camera_label)
        middle_layout.addWidget(camera_frame)

        layout.addLayout(middle_layout)

        self.graph_canvas_bottom = create_line_graph()
        self.graph_canvas_bottom.setFixedSize(1350, 400)
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.graph_canvas_bottom)
        bottom_layout.addLayout(self.create_gauge_column(["Humedad Aire", "Temp. Aire", "Nivel Agua"]))
        layout.addLayout(bottom_layout)

        # Inicializar Picamera
        self.picam = Picamera2()
        config = self.picam.create_preview_configuration(main={"size": (640, 480)})
        self.picam.configure(config)
        self.picam.start()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_camera_frame)
        self.timer.start(30)

    def update_camera_frame(self):
        frame = self.picam.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg).scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.camera_label.setPixmap(pixmap)

    def liberar_camara(self):
        if hasattr(self, "picam"):
            try:
                self.timer.stop()
                self.picam.stop()
                self.picam.close()
                print("📷 Cámara liberada correctamente.")
            except Exception as e:
                print("⚠️ Error al liberar la cámara:", e)

    def create_card(self, title, value, timestamp, tooltip_text):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #1f2232;
                border-radius: 25px;
                padding: 5px;
                color: white;
            }
            QLabel {
                qproperty-alignment: AlignCenter;
            }
        """)
        card.setFixedSize(250, 185)

        # Info button
        info_button = QPushButton()
        icon_i = QIcon("assets/icons/info-circle.svg")
        pixmap = icon_i.pixmap(QSize(20, 20))
        info_button.setIcon(QIcon(pixmap))
        info_button.setFixedSize(24, 24)
        info_button.setIconSize(QSize(20, 20))
        info_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                margin-left: 6px;
            }
            QPushButton:hover {
                background-color: #444;
                border-radius: 12px;
            }
        """)

        # Tooltip personalizado al hacer hover
        class InfoButtonEnterEvent:
            def __init__(self, button):
                self.button = button

            def enterEvent(self, event):
                QToolTip.showText(
                    self.button.mapToGlobal(QPoint(0, 20)),
                    tooltip_text,
                    self.button,
                    QRect(),
                    0
                )
                super(type(self.button), self.button).enterEvent(event)

        info_button.enterEvent = InfoButtonEnterEvent(info_button).enterEvent

        # Título + ícono
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 10, QFont.Bold))

        title_info_layout = QHBoxLayout()
        title_info_layout.setAlignment(Qt.AlignHCenter)
        title_info_layout.setSpacing(4)
        title_info_layout.addWidget(title_label)
        title_info_layout.addWidget(info_button)

        # Centro del contenido
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 18, QFont.Bold))
        value_label.setMinimumHeight(40)
        value_label.setAlignment(Qt.AlignCenter)

        time_label = QLabel(timestamp)
        time_label.setFont(QFont("Arial", 9))
        time_label.setAlignment(Qt.AlignCenter)

        # Guardamos referencias en self.card_labels
        if not hasattr(self, "card_labels"):
            self.card_labels = {}
        self.card_labels[title] = (value_label, time_label)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.addLayout(title_info_layout)
        main_layout.addWidget(value_label)
        main_layout.addWidget(time_label)
        card.setLayout(main_layout)
        return card

    def recibir_datos_sensores(self, data):
        self.sensor_data.update(data)  # Mantener unificado el estado

        mapping = {
            "Temperatura del agua": ("temp_agua", "°C"),
            "Nivel pH del agua": ("ph", " pH"),
            "Nivel ORP": ("orp", " mV"),
            "Nivel del agua": ("nivel_agua", " cm"),
            "Temperatura del aire": ("temp_aire", "°C"),
            "Humedad del aire": ("humedad_aire", "%")
        }

        for title, (key, unidad) in mapping.items():
            if title in self.card_labels:
                value_label, time_label = self.card_labels[title]
                valor = self.sensor_data.get(key)
                hora = self.sensor_data.get("hora", "—")
                if valor is not None:
                    value_label.setText(f"{valor:.2f} {unidad}")
                else:
                    value_label.setText("N/D")
                time_label.setText(hora)

        # Gauges
        if "ph" in self.sensor_data and "PH Agua" in self.gauges:
            self.gauges["PH Agua"].set_value(self.sensor_data["ph"])
        if "orp" in self.sensor_data and "ORP" in self.gauges:
            self.gauges["ORP"].set_value(self.sensor_data["orp"])
        if "temp_agua" in self.sensor_data and "Temp. Agua" in self.gauges:
            self.gauges["Temp. Agua"].set_value(self.sensor_data["temp_agua"])
        if "nivel_agua" in self.sensor_data and "Nivel Agua" in self.gauges:
            self.gauges["Nivel Agua"].set_value(self.sensor_data["nivel_agua"])
        if "temp_aire" in self.sensor_data and "Temp. Aire" in self.gauges:
            self.gauges["Temp. Aire"].set_value(self.sensor_data["temp_aire"])
        if "humedad_aire" in self.sensor_data and "Humedad Aire" in self.gauges:
            self.gauges["Humedad Aire"].set_value(self.sensor_data["humedad_aire"])




    def create_gauge_column(self, titles):
        gauges_layout = QVBoxLayout()
        gauge_frame = QFrame()
        gauge_frame.setFixedWidth(150)
        gauge_frame.setStyleSheet("background-color: #1f2232; border-radius: 20px;")
        gauge_frame_layout = QVBoxLayout()
        for title in titles:
            gauge_frame_layout.addWidget(self.create_circular_gauge(title))
        gauge_frame.setLayout(gauge_frame_layout)
        gauges_layout.addWidget(gauge_frame)
        return gauges_layout

    def create_circular_gauge(self, title="Gauge"):
        class CircularGauge(QWidget):
            def __init__(self, title="Gauge"):
                super().__init__()
                self.value = 0.0
                self.title = title
                self.setFixedSize(125, 125)
                self.timer = QTimer(self)
                self.timer.timeout.connect(self.update)
                self.timer.start(1000)

            def set_value(self, new_value):
                self.value = new_value if new_value is not None else 0
                self.valid = new_value is not None
                self.update()

            def paintEvent(self, event):
                painter = QPainter(self)
                painter.setRenderHint(QPainter.Antialiasing)
                rect = self.rect()
                center = rect.center()
                radius = min(rect.width(), rect.height()) / 2 - 10

                # Fondo
                painter.setBrush(QColor("#1f2232"))
                painter.setPen(Qt.NoPen)
                painter.drawRect(rect)

                # Título
                painter.setPen(Qt.white)
                font = QFont("Candara", 8)
                painter.setFont(font)
                painter.drawText(0, 35, rect.width(), 20, Qt.AlignCenter, self.title)

                # Arco
                gradient = QConicalGradient(center, -90)  # -90 grados es hacia arriba
                gradient.setColorAt(0.0, QColor("#FF8800"))   # Naranja (empieza desde la derecha)
                gradient.setColorAt(1/6, QColor("#FF8800"))   # Verde (parte superior)
                gradient.setColorAt(2/6, QColor("#00FF00"))   # Naranja (izquierda)
                gradient.setColorAt(3/6, QColor("#00FF00"))   # Naranja (izquierda)
                gradient.setColorAt(4/6, QColor("#00FF00"))   # Naranja (izquierda)
                gradient.setColorAt(5/6, QColor("#FF8800"))   # Naranja (izquierda)
                gradient.setColorAt(1.0, QColor("#FF8800"))   # Cierra ciclo con naranja


                arc_rect = QRect(
                    int(center.x() - radius), int(center.y() - radius),
                    int(2 * radius), int(2 * radius)
                )

                painter.setPen(QPen(QBrush(gradient), 12))
                painter.drawArc(arc_rect, 225 * 16, -270 * 16)

                # Aguja
                if getattr(self, "valid", True):  # Solo si el valor es válido
                    angle = 225 - (self.value - 15) / 20 * 270
                    angle_rad = math.radians(angle)

                    needle_length = radius - 10
                    needle_x = center.x() + needle_length * math.cos(angle_rad)
                    needle_y = center.y() - needle_length * math.sin(angle_rad)
                    painter.setPen(QPen(Qt.white, 2))
                    painter.drawLine(center, QPointF(needle_x, needle_y))

                # Valor
                font.setPointSize(10)
                painter.setFont(font)
                painter.drawText(0, int(center.y() + radius / 2), rect.width(), 40, Qt.AlignCenter, f"{self.value:.1f}")

        gauge = CircularGauge(title)
        self.gauges[title] = gauge  # ⬅️ Guardamos la instancia
        return gauge