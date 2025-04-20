from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class DevicesAppAdmin(QWidget):
    def __init__(self, ventana_login, embed=False):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("Pantalla de Dispositivos")
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Candara", 16))
        layout.addWidget(label)
        self.setLayout(layout)