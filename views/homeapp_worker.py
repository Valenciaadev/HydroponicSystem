from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy, QStackedLayout
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QSize
from views.summaryapp_worker import SummaryAppWorker
from views.actuatorsapp_worker import ActuatorsAppWorker
from views.sensorsapp_worker import SensorsAppWorker
from views.devicesapp_worker import DevicesAppWorker
from views.historyapp_worker import HistoryAppWorker

class HomeappWorker(QWidget):
    def __init__(self, ventana_login):
        super().__init__()
        self.ventana_login = ventana_login
        self.setWindowTitle("Panel Principal")
        self.showFullScreen()

        layout_principal = QHBoxLayout()

        # Stacked layout para cambiar entre vistas
        self.stacked_layout = QStackedLayout()
        
        # Crear las vistas de cada sección
        # self.inicio_widget = self.pantalla_inicio()
        self.inicio_widget = SummaryAppWorker(self.ventana_login, embed=True)
        self.actuadores_widget = ActuatorsAppWorker(self.ventana_login, embed=True)
        self.sensores_widget = SensorsAppWorker(self.ventana_login, embed=True)
        self.dispositivos_widget = DevicesAppWorker(self.ventana_login, embed=True)
        self.historial_widget = HistoryAppWorker(self.ventana_login, embed=True)

        # Agregar vistas al stacked layout
        self.stacked_layout.addWidget(self.inicio_widget)
        self.stacked_layout.addWidget(self.actuadores_widget)
        self.stacked_layout.addWidget(self.sensores_widget)
        self.stacked_layout.addWidget(self.dispositivos_widget)
        self.stacked_layout.addWidget(self.historial_widget)
        
        self.stacked_layout.setCurrentIndex(0)
        
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
                font: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2471a3;
            }
        """

        btn_home = QPushButton(" Inicio")
        btn_home.setStyleSheet(btn_style)
        btn_home.clicked.connect(lambda: self.stacked_layout.setCurrentIndex(0))
        btn_home.setIcon(QIcon("assets/icons/home-white.svg"))
        btn_home.setIconSize(QSize(24, 24))

        btn_actuators = QPushButton(" Actuadores")
        btn_actuators.setStyleSheet(btn_style)
        btn_actuators.clicked.connect(lambda: self.stacked_layout.setCurrentIndex(1))
        btn_actuators.setIcon(QIcon("assets/icons/actuators-white.svg"))
        btn_actuators.setIconSize(QSize(24, 24))

        btn_sensors = QPushButton(" Sensores")
        btn_sensors.setStyleSheet(btn_style)
        btn_sensors.clicked.connect(lambda: self.stacked_layout.setCurrentIndex(2))
        btn_sensors.setIcon(QIcon("assets/icons/sensors-white.svg"))
        btn_sensors.setIconSize(QSize(24, 24))

        btn_devices = QPushButton(" Dispositivos")
        btn_devices.setStyleSheet(btn_style)
        btn_devices.clicked.connect(lambda: self.stacked_layout.setCurrentIndex(3))
        btn_devices.setIcon(QIcon("assets/icons/devices-white.svg"))
        btn_devices.setIconSize(QSize(24, 24))
        
        btn_history = QPushButton(" Historial")
        btn_history.setStyleSheet(btn_style)
        btn_history.clicked.connect(lambda: self.stacked_layout.setCurrentIndex(4))
        btn_history.setIcon(QIcon("assets/icons/history-white.svg"))
        btn_history.setIconSize(QSize(24, 24))

        btn_exit = QPushButton(" Cerrar sesión")
        btn_exit.setStyleSheet(btn_style)
        btn_exit.setIcon(QIcon("assets/icons/log_out-white.svg"))
        btn_exit.setIconSize(QSize(24, 24))
        btn_exit.clicked.connect(self.log_out)

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

        sidebar.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Fixed))
        sidebar.addWidget(btn_home)
        sidebar.addWidget(btn_actuators)
        sidebar.addWidget(btn_sensors)
        sidebar.addWidget(btn_devices)
        sidebar.addWidget(btn_history)
        sidebar.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))
        sidebar.addWidget(btn_exit)
        sidebar.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Fixed))

        layout_principal.addWidget(sidebar_widget)

        # Contenido principal
        content_widget = QWidget()
        content_widget.setLayout(self.stacked_layout)
        layout_principal.addWidget(content_widget)

        self.setLayout(layout_principal)

    def log_out(self):
        self.ventana_login.show()
        self.close()