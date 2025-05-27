from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from views.seleccion_usuario import TitleBar
from views.summaryapp_admin import SummaryAppAdmin
from views.actuatorsapp_admin import ActuatorsAppAdmin
from views.sensorsapp_admin import SensorsAppAdmin
from views.historyapp_admin import HistoryAppAdmin
from views.managment_users_admin import ManagmentAppAdmin
from views.gestionhortalizas_admin import GestionHortalizasAppAdmin
from models.serial_thread import SerialReaderThread

class HomeappAdmin(QWidget):
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

        # Logo grande en la parte superior izquierda
        logo_label = QLabel()
        logo_pixmap = QPixmap("assets/img/logo.png")
        logo_label.setPixmap(logo_pixmap.scaled(462, 168, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        logo_label.setStyleSheet("padding: 10px; margin-bottom: 20px;")
        left_container.addWidget(logo_label)

        # Sidebar centrado verticalmente pero más arriba
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

        # Etiquetas de sección
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

        self.btn_users = QPushButton(" Gestionar usuarios")
        self.btn_users.setCheckable(True)
        self.btn_users.setStyleSheet(btn_style)
        self.btn_users.clicked.connect(lambda: self.change_view(4))
        self.btn_users.setIcon(QIcon("assets/icons/users-solid.svg"))
        self.btn_users.setIconSize(QSize(24, 24))

        self.btn_hortalizas = QPushButton(" Hortalizas")
        self.btn_hortalizas.setCheckable(True)
        self.btn_hortalizas.setStyleSheet(btn_style)
        self.btn_hortalizas.clicked.connect(lambda: self.change_view(5))
        self.btn_hortalizas.setIcon(QIcon("assets/icons/sapling.svg"))
        self.btn_hortalizas.setIconSize(QSize(24, 24))
        # Espacio antes del botón de cerrar sesión
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        
        # Botones del sidebar (nuevo botón de hortalizas primero)

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

        # Orden de los botones en el sidebar
        sidebar.addWidget(label_vistas)
        sidebar.addWidget(self.btn_home)
        sidebar.addWidget(self.btn_actuators)
        sidebar.addWidget(self.btn_sensors)
        sidebar.addWidget(self.btn_history)
        sidebar.addWidget(self.btn_users)

        # Separador flexible
        sidebar.addItem(spacer)

        # Sección de configuración
        sidebar.addWidget(label_configuracion)
        sidebar.addWidget(self.btn_hortalizas)
        sidebar.addWidget(btn_exit)


        sidebar_container.addSpacing(50)
        sidebar_container.addWidget(sidebar_widget)
        sidebar_container.addStretch(0)
        
        left_container.addLayout(sidebar_container)
        layout_principal.addLayout(left_container)

        # Stacked layout para cambiar entre vistas
        self.stacked_layout = QStackedLayout()
        
        # Crear las vistas de cada sección (nueva vista de hortalizas primero)
        self.inicio_widget = SummaryAppAdmin(self.ventana_login, embed=True)
        self.actuadores_widget = ActuatorsAppAdmin(self.ventana_login, embed=True)
        self.sensores_widget = SensorsAppAdmin(self.ventana_login, embed=True)
        self.historial_widget = HistoryAppAdmin(self.ventana_login, embed=True)
        self.gestion_usuarios_widget = ManagmentAppAdmin(self.ventana_login, embed=True)
        self.hortalizas_widget = GestionHortalizasAppAdmin(self.ventana_login, embed=True)
        
        # Agregar vistas al stacked layout (nueva vista en posición 0)
        self.stacked_layout.addWidget(self.inicio_widget)
        self.stacked_layout.addWidget(self.actuadores_widget)
        self.stacked_layout.addWidget(self.sensores_widget)
        self.stacked_layout.addWidget(self.historial_widget)
        self.stacked_layout.addWidget(self.gestion_usuarios_widget)
        self.stacked_layout.addWidget(self.hortalizas_widget)
        self.stacked_layout.setCurrentIndex(0)  # Inicia en Inicio (índice 1)

        # Contenido principal
        content_widget = QWidget()
        content_widget.setLayout(self.stacked_layout)
        layout_principal.addWidget(content_widget)

        self.setLayout(layout_principal)
        
    # def log_out(self):
        #self.ventana_login.show()
        # self.close()

        self.serial_thread = SerialReaderThread()
        self.serial_thread.datos_actualizados.connect(self.inicio_widget.recibir_datos_sensores)
        self.serial_thread.start()
        
    # def log_out(self):
        #self.ventana_login.show()
        # self.close()

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
        cancel_button.setStyleSheet("background-color: gray; color: white; padding: 5px; border-radius: 5px;")
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

        # 🛑 Detener hilo serial si está corriendo
        if hasattr(self, 'serial_thread'):
            self.serial_thread.stop()
            self.serial_thread.quit()
            self.serial_thread.wait()
            print("🔌 Hilo serial detenido correctamente al cerrar sesión.")

        self.ventana_login.show()
        self.close()

    def change_view(self, index):
        """Cambia la vista y actualiza el botón activo"""
        self.stacked_layout.setCurrentIndex(index)
        
        # Desmarcar todos los botones primero
        self.btn_hortalizas.setChecked(False)
        self.btn_home.setChecked(False)
        self.btn_actuators.setChecked(False)
        self.btn_sensors.setChecked(False)
        self.btn_history.setChecked(False)
        self.btn_users.setChecked(False)
        
        # Marcar el botón activo
        if index == 0:
            self.btn_home.setChecked(True)
        elif index == 1:
            self.btn_actuators.setChecked(True)
        elif index == 2:
            self.btn_sensors.setChecked(True)
        elif index == 3:
            self.btn_history.setChecked(True)
        elif index == 4:
            self.btn_users.setChecked(True)
        elif index == 5:
            self.btn_hortalizas.setChecked(True)