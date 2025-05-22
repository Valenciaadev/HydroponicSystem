from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from models.database import create_line_graph, create_bar_graph
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

class SummaryAppAdmin(QWidget):
    def __init__(self, ventana_login, embed=False):
        super().__init__()

        QToolTip.setFont(QFont("Arial", 12))
        QApplication.instance().setStyleSheet("""
            QToolTip {
                font-size: 12pt;
                color: white;
                background-color: #1f2232;
                border: 1px solid white;
                padding: 4px;
                border-radius: 6px;
                min-width: 300px;
                text-justify: auto;
            }
        """)

        outer_layout = QVBoxLayout(self)

        # Frame contenedor principal con fondo #27243A
        container_frame = QFrame()
        container_frame.setStyleSheet("background-color: #27243A; border-radius: 10px;")
        container_layout = QVBoxLayout(container_frame)
        outer_layout.addWidget(container_frame)

        # 1. Sección superior: Sensores y cámara
        top_section = QHBoxLayout()

        # 1.1 Columnas de sensores (izquierda)
        sensors_layout = QVBoxLayout()

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
                "Otro sensor", "N/A", "26/2 21:23:04",
                "<b>Otro Sensor</b><br>Este es un espacio reservado para sensores adicionales del sistema."
            ),
            (
                "Nivel del agua", "0 bool", "26/2 21:23:04",
                "<b>Nivel del Agua</b><br>"
                "Debe cubrir completamente las raíces sin llegar al tallo.<br>"
                "Se recomienda mantener un nivel constante para evitar estrés hídrico."
            ),
        ]

        for i in range(0, len(cards_info), 3):
            row_layout = QHBoxLayout()
            for card_data in cards_info[i:i+3]:
                row_layout.addWidget(self.create_card(*card_data))
            sensors_layout.addLayout(row_layout)

        sensors_widget = QWidget()
        sensors_widget.setLayout(sensors_layout)

        # 1.2 Vista de cámara (derecha)
        camera_frame = QFrame()
        camera_frame.setFixedWidth(800)
        camera_frame.setStyleSheet("""
            background-color: #1f2232;
            border: 2px solid #444444;
            border-radius: 20px;
        """)
        camera_layout = QVBoxLayout(camera_frame)
        camera_layout.setContentsMargins(10, 10, 10, 10)

        camera_label = QLabel("Vista Cámara")
        camera_label.setStyleSheet("color: white; font-size: 16px;")
        camera_label.setAlignment(Qt.AlignCenter)
        camera_layout.addWidget(camera_label)

        sensors_camera_container = QHBoxLayout()
        sensors_camera_container.addWidget(sensors_widget, stretch=3)
        sensors_camera_container.addStretch(1)
        sensors_camera_container.addWidget(camera_frame, stretch=2)

        container_layout.addLayout(sensors_camera_container)

        # 2. Sección inferior: Gráficas
        graphs_frame = QFrame()
        graphs_frame.setFixedHeight(380)
        graphs_frame.setStyleSheet("""
            background-color: #1f2232;
            border: 2px solid #444444;
            border-radius: 20px;
        """)
        graphs_layout = QHBoxLayout(graphs_frame)

        self.graph_canvas_left = create_line_graph()
        self.graph_canvas_left.setFixedSize(650, 280)
        graphs_layout.addWidget(self.graph_canvas_left)

        self.graph_canvas_right = create_bar_graph()
        self.graph_canvas_right.setFixedSize(650, 280)
        graphs_layout.addWidget(self.graph_canvas_right)

        container_layout.addWidget(graphs_frame)

    def create_card(self, title, value, timestamp, tooltip_text):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #1f2232;
                border-radius: 25px;
                padding: 10px;
                color: white;
                margin-right: 5px;
                margin-bottom: 5px;
            }
            QLabel {
                qproperty-alignment: AlignCenter;
            }
        """)
        card.setFixedSize(280, 310)

        class InfoButton(QPushButton):
            def __init__(self, tooltip, parent=None):
                super().__init__(parent)
                self.tooltip = tooltip
                self.setIcon(QIcon("assets/icons/info-circle.svg"))
                self.setFixedSize(24, 24)
                self.setIconSize(QSize(20, 20))
                self.setStyleSheet("""
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

            def enterEvent(self, event):
                QToolTip.showText(
                    self.mapToGlobal(QPoint(0, 24)),
                    self.tooltip,
                    self,
                    QRect(),
                    5000
                )
                super().enterEvent(event)

        info_button = InfoButton(tooltip_text)

        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 11, QFont.Bold))

        title_info_layout = QHBoxLayout()
        title_info_layout.setAlignment(Qt.AlignHCenter)
        title_info_layout.setSpacing(4)
        title_info_layout.addWidget(title_label)
        title_info_layout.addWidget(info_button)

        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 18, QFont.Bold))
        value_label.setMinimumHeight(40)
        value_label.setAlignment(Qt.AlignCenter)

        time_label = QLabel(timestamp)
        time_label.setFont(QFont("Arial", 9))
        time_label.setAlignment(Qt.AlignCenter)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.addLayout(title_info_layout)
        main_layout.addWidget(value_label)
        main_layout.addWidget(time_label)
        card.setLayout(main_layout)

        return card
