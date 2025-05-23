from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from models.database import create_line_graph
from models.database import create_bar_graph
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import random
import math

class SummaryAppAdmin(QWidget):
    def __init__(self, ventana_login, embed=False):
        super().__init__()

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
                "Temperatura del aire", "24°", "26/2 21:23:04",
                "<b>Temperatura del Aire</b><br>"
                "Ideal entre <b>18°C y 24°C</b> para el crecimiento óptimo de lechugas.<br>"
                "Evita temperaturas mayores a 27°C para prevenir estrés térmico."
            ),
            (
                "Humedad del aire", "61.2", "26/2 21:23:04",
                "<b>Humedad Relativa del Aire</b><br>"
                "Rango ideal: <b>50% a 70%</b>.<br>"
                "Niveles adecuados reducen la transpiración excesiva y promueven la fotosíntesis."
            ),
            (
                "Temperatura del agua", "26°", "26/2 21:23:04",
                "<b>Temperatura del Agua</b><br>"
                "Ideal entre <b>18°C y 22°C</b>.<br>"
                "Temperaturas superiores a 24°C pueden reducir el oxígeno disuelto, afectando las raíces."
            ),
            (
                "Nivel pH del agua", "5 pH", "26/2 21:23:04",
                "<b>Nivel de pH del Agua</b><br>"
                "Rango óptimo: <b>5.5 a 6.5</b> para lechugas.<br>"
                "Valores fuera de este rango dificultan la absorción de nutrientes."
            ),
            (
                "Nivel ORP del agua", "320 mV", "26/2 21:23:04",
                "<b>Potencial Redox (ORP)</b><br>"
                "Rango ideal para lechugas: <b>250 mV a 400 mV</b>.<br>"
                "Un ORP dentro de este rango indica un buen equilibrio entre oxidantes y reductores, "
                "lo cual favorece la absorción de nutrientes y evita la proliferación de microorganismos indeseados."
            ),
            (
                "Nivel del agua", "0 bool", "26/2 21:23:04",
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
        middle_layout.addLayout(self.create_gauge_column(["Temp. Aire", "Humedad Aire", "Temp. Agua"]))

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
        camera_frame.setStyleSheet("background-color: #1f2232; border: 2px solid #444444; border-radius: 20px;")
        camera_label = QLabel("Vista Cámara", camera_frame)
        camera_label.setStyleSheet("color: white;")
        camera_label.setAlignment(Qt.AlignCenter)
        middle_layout.addWidget(camera_frame)

        layout.addLayout(middle_layout)

        # SECCIÓN 3 PARTE INFERIOR
        bottom_layout = QHBoxLayout()

        # 3.1 INICIO DE LA GRÁFICA DE LÍNEAS //////////////////////
        self.graph_canvas_bottom = create_line_graph()
        self.graph_canvas_bottom.setFixedSize(1350, 400)
        bottom_layout.addWidget(self.graph_canvas_bottom)
        # 3.1 FIN DE LA GRÁFICA DE LÍNEAS //////////////////////

        # 3.2 Gauges derechos
        bottom_layout.addLayout(self.create_gauge_column(["PH Agua", "Nivel Agua", "ORP"]))

        layout.addLayout(bottom_layout)

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

        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.addLayout(title_info_layout)
        main_layout.addWidget(value_label)
        main_layout.addWidget(time_label)
        card.setLayout(main_layout)
        return card

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
                self.value = 24.1
                self.title = title
                self.setFixedSize(125, 125)
                self.timer = QTimer(self)
                self.timer.timeout.connect(self.update_value)
                self.timer.start(2000)

            def update_value(self):
                self.value = round(random.uniform(15.0, 35.0), 1)
                self.update()

            def paintEvent(self, event):
                painter = QPainter(self)
                painter.setRenderHint(QPainter.Antialiasing)
                rect = self.rect()
                center = rect.center()
                radius = min(rect.width(), rect.height()) / 2 - 10

                painter.setBrush(QColor("#1f2232"))
                painter.setPen(Qt.NoPen)
                painter.drawRect(rect)

                painter.setPen(Qt.white)
                font = QFont("Candara", 8)
                painter.setFont(font)
                painter.drawText(0, 20, rect.width(), 20, Qt.AlignCenter, self.title)

                gradient = QConicalGradient(center, -90)
                gradient.setColorAt(0.0, Qt.green)
                gradient.setColorAt(0.5, Qt.cyan)
                gradient.setColorAt(1.0, Qt.green)
                painter.setPen(QPen(QBrush(gradient), 12))
                arc_rect = QRect(
                    int(center.x() - radius), int(center.y() - radius),
                    int(2 * radius), int(2 * radius)
                )
                painter.drawArc(arc_rect, 45 * 16, 270 * 16)

                angle = 45 + (self.value - 15) / 20 * 270
                needle_length = radius - 10
                needle_x = center.x() + needle_length * math.cos(math.radians(angle - 90))
                needle_y = center.y() + needle_length * math.sin(math.radians(angle - 90))
                painter.setPen(QPen(Qt.white, 2))
                painter.drawLine(center, QPointF(needle_x, needle_y))

                font.setPointSize(10)
                painter.setFont(font)
                painter.drawText(0, int(center.y() - radius + 50), rect.width(), 40, Qt.AlignCenter, f"{self.value:.1f}")

        return CircularGauge(title)