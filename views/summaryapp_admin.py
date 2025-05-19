from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame
from PyQt5.QtCore import Qt, QTimer, QPointF, QRect
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QConicalGradient, QBrush
from models.database import create_line_graph
from models.database import create_bar_graph
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import random
import math

class SummaryAppAdmin(QWidget):
    def __init__(self, ventana_login, embed=False):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        # 1. Tarjetas superiores
        top_cards_layout = QHBoxLayout()
        top_cards_layout.setSpacing(20)
        
        cards_info = [
            ("Temperatura del aire", "24°", "26/2 21:23:04"),
            ("Humedad del aire", "61.2", "26/2 21:23:04"),
            ("Temperatura del agua", "26°", "26/2 21:23:04"),
            ("Nivel pH del agua", "5 pH", "26/2 21:23:04"),
            ("Nivel del agua", "0 bool", "26/2 21:23:04"),
        ]
        for title, value, timestamp in cards_info:
            card = self.create_card(title, value, timestamp)
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
            background-color: #1e2b3c;
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
        camera_frame.setStyleSheet("background-color: #1e2b3c; border: 2px solid #444444; border-radius: 20px;")
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
        bottom_layout.addLayout(self.create_gauge_column(["pH Agua", "Nivel Agua", "Otro"]))

        layout.addLayout(bottom_layout)

    def create_card(self, title, value, timestamp):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #1e2b3c;
                border-radius: 25px;
                padding: 10px;
                color: white;
            }
            QLabel {
                qproperty-alignment: AlignCenter;
            }
        """)
        card.setFixedSize(260, 185)

        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignCenter)

        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 11, QFont.Bold))

        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 18, QFont.Bold))
        value_label.setMinimumHeight(40)

        time_label = QLabel(timestamp)
        time_label.setFont(QFont("Arial", 9))

        vbox.addWidget(title_label)
        vbox.addWidget(value_label)
        vbox.addWidget(time_label)

        card.setLayout(vbox)
        return card

    def create_gauge_column(self, titles):
        gauges_layout = QVBoxLayout()
        gauge_frame = QFrame()
        gauge_frame.setFixedWidth(150)
        gauge_frame.setStyleSheet("background-color: #1e2b3c; border-radius: 20px;")
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

                painter.setBrush(QColor("#1e2b3c"))
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