from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy
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

        btn_style = """
            QPushButton {
                background-color: #2B2642;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2471a3;
            }
        """
        
        btn_home = QPushButton("Inicio")
        btn_home.setStyleSheet(btn_style)
        
        btn_actuators = QPushButton("Actuadores")
        btn_actuators.setStyleSheet(btn_style)
        btn_actuators.clicked.connect(self.ir_a_actuadores)
        
        btn_sensors = QPushButton("Sensores")
        btn_sensors.setStyleSheet(btn_style)
        
        btn_devices = QPushButton("Dispositivos")
        btn_devices.setStyleSheet(btn_style)
        
        btn_config = QPushButton("Configuración")
        btn_config.setStyleSheet(btn_style)
        
        btn_exit = QPushButton("Salir")
        btn_exit.setStyleSheet(btn_style)
        btn_exit.clicked.connect(self.cerrar_sesion)

        # Estructura del sidebar
        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar)
        sidebar_widget.setFixedWidth(200)
        sidebar_widget.setFixedHeight(550)
        sidebar_widget.setStyleSheet("""
            background-color: #2c3e50;
            color: white;
            border-top-right-radius: 15px;
            border-bottom-right-radius: 15px;
        """)

        # Espacio superior más pequeño
        sidebar.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Botones principales
        sidebar.addWidget(btn_home)
        sidebar.addWidget(btn_actuators)
        sidebar.addWidget(btn_sensors)
        sidebar.addWidget(btn_devices)
        sidebar.addWidget(btn_config)

        # Espacio entre botones y "Salir"
        sidebar.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))
        sidebar.addWidget(btn_exit)

        # Espacio inferior
        sidebar.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Contenido principal
        content = QLabel("Bienvenido al panel de administrador")
        content.setAlignment(Qt.AlignCenter)
        content.setFont(QFont("Candara", 16))

        layout_principal.addWidget(sidebar_widget)
        layout_principal.addWidget(content)

        self.setLayout(layout_principal)

    def ir_a_actuadores(self):
        from views.actuatorsapp_admin import ActuatorsAppAdmin
        self.close()
        self.actuators = ActuatorsAppAdmin(self.ventana_login)
        self.actuators.show()
        
    def cerrar_sesion(self):
        self.ventana_login.show()
        self.close()