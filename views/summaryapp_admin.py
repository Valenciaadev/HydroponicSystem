from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import random
import math


class SummaryAppAdmin(QWidget):
    def __init__(self, ventana_login, embed=False):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Layout superior de tarjetas
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
        
        # Layout para gráficas debajo de las cartas
        graphs_layout = QHBoxLayout()
        graphs_layout.setSpacing(30)

        # Gráfica izquierda
        left_graph = QFrame()
        left_graph.setStyleSheet("background-color: #102020; border-radius: 15px;")
        left_graph.setMinimumHeight(200)
        left_graph_layout = QVBoxLayout()
        left_graph_label = QLabel("Gráfica 1 - Ejemplo")
        left_graph_label.setStyleSheet("color: white; font-weight: bold;")
        left_graph_label.setAlignment(Qt.AlignCenter)
        left_graph_layout.addWidget(left_graph_label)
        # Aquí puedes insertar un gráfico real o un QLabel con QPixmap temporalmente
        left_graph.setLayout(left_graph_layout)

        # Gráfica derecha
        right_graph = QFrame()
        right_graph.setStyleSheet("background-color: #102020; border-radius: 15px;")
        right_graph.setMinimumHeight(200)
        right_graph_layout = QVBoxLayout()
        right_graph_label = QLabel("Gráfica 2 - Ejemplo")
        right_graph_label.setStyleSheet("color: white; font-weight: bold;")
        right_graph_label.setAlignment(Qt.AlignCenter)
        right_graph_layout.addWidget(right_graph_label)
        right_graph.setLayout(right_graph_layout)

        graphs_layout.addWidget(left_graph)
        graphs_layout.addWidget(right_graph)

        layout.addLayout(graphs_layout)
        

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