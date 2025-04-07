from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QFont, QPixmap
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
        
        logo_label = QLabel()
        pixmap = QPixmap("/assets/img/hs-icon.png")  # Cambia por la ruta de tu imagen
        pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        
        btn_inicio = QPushButton("Inicio")
        btn_inicio.setStyleSheet("""
            QPushButton {
                padding: 10px;
                font-size: 14px;
                color: white;
                border: 2px solid #00f7ff;
                border-radius: 20px;
                background-color: transparent;
                font: bold;
                min-width: 140px;
            }
            QPushButton:hover {
                background-color: rgba(0, 247, 255, 0.1);
            }
            QPushButton:pressed {
                background-color: rgba(0, 247, 255, 0.3);
            }
        """)

        btn_actuators = QPushButton("Actuadores")
        btn_actuators.setStyleSheet(btn_inicio.styleSheet())
        
        btn_sensors = QPushButton("Sensores")
        btn_sensors.setStyleSheet(btn_inicio.styleSheet())
        
        btn_devices = QPushButton("Dispositivos")
        btn_devices.setStyleSheet(btn_inicio.styleSheet())
        
        btn_history = QPushButton("Historial")
        btn_history.setStyleSheet(btn_inicio.styleSheet())
        
        btn_config_users = QPushButton("Gestion de usuarios")
        btn_config_users.setStyleSheet(btn_inicio.styleSheet())
        
        center_layout = QVBoxLayout()
        center_layout.setAlignment(Qt.AlignVCenter)
        center_layout.setSpacing(15)
        
        center_layout.addWidget(logo_label)
        center_layout.addWidget(btn_inicio)
        center_layout.addWidget(btn_sensors)
        center_layout.addWidget(btn_devices)
        center_layout.addWidget(btn_history)
        center_layout.addWidget(btn_config_users)

        center_widget = QWidget()
        center_widget.setLayout(center_layout)
        
        btn_salir = QPushButton("Salir")
        btn_salir.setStyleSheet(btn_inicio.styleSheet())
        btn_salir.clicked.connect(self.cerrar_sesion)

        # Empaquetar layouts en widget de sidebar
        sidebar.addStretch()
        sidebar.addWidget(center_widget)
        sidebar.addStretch()
        sidebar.addWidget(btn_salir)
        
        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar)
        sidebar_widget.setFixedWidth(200)
        sidebar_widget.setFixedHeight(900)
        sidebar_widget.setStyleSheet("""
            background-color: #2c3e50;
            color: white;
            border-top-right-radius: 15px;
            border-bottom-right-radius: 15px;
        """)

        # Contenido principal
        contenido = QLabel("Bienvenido al panel de administrador")
        contenido.setAlignment(Qt.AlignCenter)
        contenido.setFont(QFont("Candara", 16))

        layout_principal.addWidget(sidebar_widget)
        layout_principal.addWidget(contenido)

        self.setLayout(layout_principal)
        
    def cerrar_sesion(self):
        self.ventana_login.show()
        self.close()