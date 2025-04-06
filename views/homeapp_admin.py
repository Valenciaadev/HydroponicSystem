from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class HomeappAdmin(QWidget):
    def __init__(self, ventana_login):
        super().__init__()
        self.ventana_login = ventana_login
        self.setWindowTitle("Panel Principal")
        self.showFullScreen()

        layout_principal = QHBoxLayout()
        
        # Sidebar
        sidebar = QVBoxLayout()
        sidebar.setContentsMargins(10, 10, 10, 10)
        sidebar.setSpacing(20)

        btn_inicio = QPushButton("Inicio")
        btn_inicio.setStyleSheet("padding: 10px; font-size: 14px;")
        btn_config = QPushButton("Configuración")
        btn_config.setStyleSheet("padding: 10px; font-size: 14px;")
        btn_salir = QPushButton("Salir")
        btn_salir.setStyleSheet("padding: 10px; font-size: 14px;")
        btn_salir.clicked.connect(self.cerrar_sesion)

        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar)
        sidebar_widget.setFixedWidth(200)
        sidebar_widget.setStyleSheet("background-color: #2c3e50; color: white;")

        sidebar.addWidget(btn_inicio)
        sidebar.addWidget(btn_config)
        sidebar.addStretch()
        sidebar.addWidget(btn_salir)

        # Contenido principal
        contenido = QLabel("Bienvenido al panel de administrador")
        contenido.setAlignment(Qt.AlignCenter)
        contenido.setFont(QFont("Candara", 16))

        layout_principal.addWidget(sidebar_widget)
        layout_principal.addWidget(contenido)

        self.setLayout(layout_principal)

    def cerrar_sesion(self):
        self.ventana_login.show()
        self.close()  # Aquí podrías volver a mostrar la ventana de login si lo deseas