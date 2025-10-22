from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from views.seleccion_usuario import TitleBar
from views.summaryapp_worker import SummaryAppWorker
from views.actuatorsapp_worker import ActuatorsAppWorker
from views.sensorsapp_worker import SensorsAppWorker
from views.historyapp_worker import HistoryAppWorker

class HomeappWorker(QWidget):
    def __init__(self, ventana_login):
        super().__init__()
        self.ventana_login = ventana_login
        self.setWindowTitle("Panel Principal")
        self.showFullScreen()

        layout_principal = QHBoxLayout()
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)

        # Contenedor para logo + sidebar
        left_container = QVBoxLayout()
        left_container.setContentsMargins(10, 50, 0, 20)
        left_container.setSpacing(0)

        # Añade espacio antes del logo
        left_container.addSpacerItem(QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap("assets/img/logo.png")
        logo_label.setPixmap(logo_pixmap.scaled(462, 168, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        logo_label.setStyleSheet("padding: 10px; margin-bottom: 20px;")
        left_container.addWidget(logo_label)

        # Sidebar
        sidebar_container = QVBoxLayout() 
        sidebar_container.setContentsMargins(0, 0, 0, 0)
        sidebar_container.setSpacing(0)
        
        sidebar = QVBoxLayout()
        sidebar.setContentsMargins(10, 20, 10, 20)
        sidebar.setSpacing(15)

        btn_style = """
            QPushButton {
                background-color: #2B2642;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
                font: bold;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #1E1B2E;
            }
            QPushButton:pressed {
                background-color: #2471a3;
            }
            QPushButton:checked {
                background-color: #546A7B;
                border-left: 5px solid #D4F5F5;
            }
        """

        label_vistas = QLabel("Vistas")
        label_vistas.setStyleSheet("color: #7FD1B9; font-weight: bold; padding-left: 4px; font-size: 16px;")
        label_vistas.setAlignment(Qt.AlignLeft)

        label_configuracion = QLabel("Configuración")
        label_configuracion.setStyleSheet("color: #7FD1B9; font-weight: bold; padding-left: 4px; font-size: 16px;")
        label_configuracion.setAlignment(Qt.AlignLeft)

        self.btn_home = QPushButton(" Inicio")
        self.btn_home.setCheckable(True)
        self.btn_home.setChecked(True)
        self.btn_home.setStyleSheet(btn_style)
        self.btn_home.clicked.connect(lambda: self.change_view(0))
        self.btn_home.setIcon(QIcon("assets/icons/home-white.svg"))
        self.btn_home.setIconSize(QSize(24, 24))

        self.btn_actuators = QPushButton(" Actuadores")
        self.btn_actuators.setCheckable(True)
        self.btn_actuators.setStyleSheet(btn_style)
        self.btn_actuators.clicked.connect(lambda: self.change_view(1))
        self.btn_actuators.setIcon(QIcon("assets/icons/actuators-white.svg"))
        self.btn_actuators.setIconSize(QSize(24, 24))

        self.btn_sensors = QPushButton(" Sensores")
        self.btn_sensors.setCheckable(True)
        self.btn_sensors.setStyleSheet(btn_style)
        self.btn_sensors.clicked.connect(lambda: self.change_view(2))
        self.btn_sensors.setIcon(QIcon("assets/icons/sensors-white.svg"))
        self.btn_sensors.setIconSize(QSize(24, 24))

        self.btn_history = QPushButton(" Historial")
        self.btn_history.setCheckable(True)
        self.btn_history.setStyleSheet(btn_style)
        self.btn_history.clicked.connect(lambda: self.change_view(3))
        self.btn_history.setIcon(QIcon("assets/icons/history-white.svg"))
        self.btn_history.setIconSize(QSize(24, 24))

        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        
        btn_exit = QPushButton(" Cerrar sesión")
        btn_exit.setStyleSheet(btn_style)
        btn_exit.setIcon(QIcon("assets/icons/log_out-white.svg"))
        btn_exit.setIconSize(QSize(24, 24))
        btn_exit.clicked.connect(self.log_out)

        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar)
        sidebar_widget.setFixedWidth(200)
        sidebar_widget.setStyleSheet("""
            background-color: #2c3e50;
            color: white;
            border-radius: 15px;
        """)

        sidebar.addWidget(label_vistas)
        sidebar.addWidget(self.btn_home)
        sidebar.addWidget(self.btn_actuators)
        sidebar.addWidget(self.btn_sensors)
        sidebar.addWidget(self.btn_history)
        sidebar.addItem(spacer)
        sidebar.addWidget(label_configuracion)
        sidebar.addWidget(btn_exit)

        sidebar_container.addSpacing(50)
        sidebar_container.addWidget(sidebar_widget)
        sidebar_container.addStretch(0)
        
        left_container.addLayout(sidebar_container)
        layout_principal.addLayout(left_container)

        # Stacked layout
        self.stacked_layout = QStackedLayout()

        if hasattr(self, "inicio_widget") and hasattr(self.inicio_widget, "liberar_camara"):
            self.inicio_widget.liberar_camara()

        def _safe_init(widget_cls, *args, **kwargs):
            try:
                return widget_cls(*args, **kwargs)
            except TypeError as e:
                # Si la clase no acepta `embed`, reintenta sin ese kwarg
                if "unexpected keyword argument 'embed'" in str(e):
                    kwargs.pop('embed', None)
                    return widget_cls(*args, **kwargs)
                raise
    
        self.inicio_widget = _safe_init(SummaryAppWorker, self.ventana_login, embed=True)
        self.actuadores_widget = _safe_init(ActuatorsAppWorker, self.ventana_login, embed=True)
        self.sensores_widget = _safe_init(SensorsAppWorker, self.ventana_login, embed=True)
        self.historial_widget = _safe_init(HistoryAppWorker, self.ventana_login, embed=True)

        self.stacked_layout.addWidget(self.inicio_widget)
        self.stacked_layout.addWidget(self.actuadores_widget)
        self.stacked_layout.addWidget(self.sensores_widget)
        self.stacked_layout.addWidget(self.historial_widget)
        self.stacked_layout.setCurrentIndex(0)

        content_widget = QWidget()
        content_widget.setLayout(self.stacked_layout)
        layout_principal.addWidget(content_widget)

        self.setLayout(layout_principal)

        # ❌ Se elimina arranque de SerialReaderThread aquí.
        # ✅ Conexiones al hilo unificado se hacen al crear la ventana desde main.py.

    def log_out(self):
        dialog = QDialog(self)
        dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        dialog.setFixedSize(450, 150)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1E1B2E;
                border: 2px solid black;
                border-radius: 10px;
                font: bold;
            }
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 5, 10, 15)
        
        title_bar = TitleBar(dialog)
        main_layout.addWidget(title_bar)
        
        content_layout = QVBoxLayout()
        
        label = QLabel("¿Está seguro que desea cerrar sesión?")
        label.setFont(QFont("Candara", 12))
        label.setStyleSheet("color: white; font:bold;")
        label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(label)
        
        button_layout = QHBoxLayout()
        
        confirm_button = QPushButton(" Aceptar")
        confirm_button.setIcon(QIcon("assets/icons/btn-accept-white.svg"))
        confirm_button.setIconSize(QSize(24, 24))
        confirm_button.setStyleSheet("""
            QPushButton {
                background-color: blue;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font: bold;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
        """)        
        confirm_button.clicked.connect(lambda: self.confirm_logout(dialog))
        button_layout.addWidget(confirm_button)
        
        cancel_button = QPushButton(" Regresar")
        cancel_button.setIcon(QIcon("assets/icons/btn-return-white.svg"))
        cancel_button.setIconSize(QSize(24, 24))
        cancel_button.setStyleSheet("""
        QPushButton {
            background-color: gray;
            color: white;
            border-radius: 5px;
            padding: 10px;
            font-size: 14px;
            font: bold;
        }
        QPushButton:hover {
            background-color: #505050;
        }
        """)
        
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_button)
        
        content_layout.addLayout(button_layout)
        main_layout.addLayout(content_layout)
        
        dialog.setLayout(main_layout)
        dialog.exec_()
        
    def confirm_logout(self, dialog):
        dialog.accept()

        # 🛑 Detener el hilo unificado SI y solo si no hay otra vista usándolo.
        try:
            if hasattr(self.ventana_login, "hydro_thread") and self.ventana_login.hydro_thread is not None:
                # Si vienes de Admin a Login, detenlo aquí:
                self.ventana_login.hydro_thread.detener()
                self.ventana_login.hydro_thread = None
        except Exception as e:
            print("⚠️ No se pudo detener HydroBoxMainThread al cerrar sesión:", e)

        self.ventana_login.show()
        self.close()

    def change_view(self, index):
        self.stacked_layout.setCurrentIndex(index)
        
        self.btn_home.setChecked(False)
        self.btn_actuators.setChecked(False)
        self.btn_sensors.setChecked(False)
        self.btn_history.setChecked(False)
        
        if index == 0:
            self.btn_home.setChecked(True)
        elif index == 1:
            self.btn_actuators.setChecked(True)
        elif index == 2:
            self.btn_sensors.setChecked(True)
        elif index == 3:
            self.btn_history.setChecked(True)