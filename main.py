import sys
import mysql.connector
from models.usuario import Usuario
from models.trabajador import Trabajador
from models.administrador import Administrador
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QStackedWidget, QWidget, QHBoxLayout, QPushButton, QLabel, QInputDialog, QLineEdit, QMessageBox
from PyQt5.QtCore import Qt, QPoint, QSize
from PyQt5.QtGui import QPalette, QColor, QIcon
from views.registro import RegistroWidget
from views.inicio_sesion_worker import InicioSesionWidget
from views.seleccion_usuario import SeleccionUsuarioWidget
from views.inicio_sesion_admin import InicioSesionAdministradorWidget
from controllers.auth_controller import hash_password
from views.homeapp_admin import HomeappAdmin
from views.homeapp_worker import HomeappWorker
from models.serial_thread import SerialReaderThread
from views.summaryapp_admin import SummaryAppAdmin
import serial
import time

# Crear un nuevo usuario trabajador
'''usuario_trabajador = Usuario(
    nombre="Alexis",
    apellido_paterno="Verduzco",
    apellido_materno="Lopez",
    email="wverduzco@ucol.mx",
    clabe=123456,
    password=hash_password("qwerty"),
    telefono="3141234567",
    tipo_usuario="trabajador"
)

id_usuario_trabajador = usuario_trabajador.guardar_en_db()

if id_usuario_trabajador:
    trabajador = Trabajador(id_usuario=id_usuario_trabajador)
    trabajador.guardar_en_db()

# Crear un nuevo usuario administrador
usuario_admin = Usuario(
    nombre="Manuel",
    apellido_paterno="Valencia",
    apellido_materno="Antonio",
    email="mvalencia18@ucol.mx",
    clabe=789101,
    password=hash_password("qwerty"),
    telefono="3147654321",
    tipo_usuario="administrador"
)

id_usuario_admin = usuario_admin.guardar_en_db()

if id_usuario_admin:
    administrador = Administrador(id_usuario=id_usuario_admin)
    administrador.guardar_en_db()
'''
class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(40)
        self.setStyleSheet("background-color: #1E1B2E; color: white;")

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 0, 10)
        layout.setSpacing(5)

        self.title = QLabel("Sistema Hidropónico")
        self.title.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.title)

        self.minimize_button = QPushButton("")
        self.minimize_button.setIcon(QIcon("assets/icons/btn-minimize-white.svg"))
        self.minimize_button.setIconSize(QSize(24, 24))
        self.minimize_button.setFixedSize(30, 30)
        self.minimize_button.setStyleSheet("background-color: transparent; color: white;")
        self.minimize_button.clicked.connect(self.parent.showMinimized)
        self.minimize_button.setCursor(Qt.PointingHandCursor)
        self.minimize_button.setStyleSheet("QPushButton:hover { background-color: blue; }")
        layout.addWidget(self.minimize_button)

        self.maximize_button = QPushButton("")
        self.maximize_button.setIcon(QIcon("assets/icons/btn-maximize-white.svg"))
        self.maximize_button.setIconSize(QSize(16, 16))
        self.maximize_button.setFixedSize(30, 30)
        self.maximize_button.setStyleSheet("background-color: transparent; color: white;")
        self.maximize_button.clicked.connect(self.toggle_maximize)
        self.maximize_button.setCursor(Qt.PointingHandCursor)
        self.maximize_button.setStyleSheet("QPushButton:hover { background-color: blue; }")
        layout.addWidget(self.maximize_button)

        self.close_button = QPushButton("")
        self.close_button.setIcon(QIcon("assets/icons/btn-close-white.svg"))
        self.close_button.setIconSize(QSize(24, 24))
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet("background-color: transparent; color: white;")
        self.close_button.clicked.connect(self.parent.close)
        self.close_button.setCursor(Qt.PointingHandCursor)
        self.close_button.setStyleSheet("QPushButton:hover { background-color: blue; }")
        layout.addWidget(self.close_button)
        
        self.setLayout(layout)
        self.drag_position = None

    def toggle_maximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.parent.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            self.parent.move(event.globalPos() - self.drag_position)
            event.accept()

class LoginRegisterApp(QDialog):
    def __init__(self):
        super().__init__()

        # Creación de la ventana sin la barra de título nativa
        self.setWindowTitle("Sistema Hidropónico")
        self.setGeometry(660, 200, 500, 500)
        self.setStyleSheet("background-color: #1E1B2E;")
        self.setWindowFlags(Qt.FramelessWindowHint)

        # self.center_window()
        
        # Creación del stack de vistas
        self.stack = QStackedWidget()

        self.register_widget = RegistroWidget(self.switch_to_login)
        self.login_widget = InicioSesionWidget(parent_app=self)
        self.user_select_widget = SeleccionUsuarioWidget(self.switch_to_admin, self.switch_to_worker)
        self.login_admin_widget = InicioSesionAdministradorWidget(parent_app=self)

        self.stack.addWidget(self.user_select_widget)
        self.stack.addWidget(self.login_admin_widget)
        self.stack.addWidget(self.register_widget)
        self.stack.addWidget(self.login_widget)

        layout = QVBoxLayout()
        self.title_bar = TitleBar(self)
        layout.addWidget(self.title_bar)
        layout.addWidget(self.stack)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Mostrar la vista de login por defecto
        self.stack.setCurrentWidget(self.user_select_widget)
        
    def mostrar_panel_admin(self):
        self.homeapp_admin = HomeappAdmin(self)
        self.serial_thread = SerialReaderThread()
        self.serial_thread.datos_actualizados.connect(self.homeapp_admin.inicio_widget.recibir_datos_sensores)
        self.serial_thread.start()

        # Mostrar la vista principal
        self.homeapp_admin.showFullScreen()
        self.hide()
    
    def mostrar_panel_worker(self):
        self.homeapp_worker = HomeappWorker(self)
        self.homeapp_worker.showFullScreen()
        self.hide()

    def switch_to_register(self):
        self.stack.setCurrentWidget(self.register_widget)

    def switch_to_login(self):
        self.stack.setCurrentWidget(self.login_widget)
    
    def switch_to_admin(self):
        # Permitir acceso directo a la pantalla de registro
        self.stack.setCurrentWidget(self.login_admin_widget)

    def switch_to_worker(self): 
        # Permitir acceso directo a la pantalla de login
        self.stack.setCurrentWidget(self.login_widget)
    
    def switch_to_user_selection(self):
        self.stack.setCurrentWidget(self.user_select_widget)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Aplicar una paleta de colores oscuros a la ventana
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#1E1B2E"))  # Fondo de la ventana
    palette.setColor(QPalette.WindowText, QColor("#FFFFFF"))  # Texto
    app.setPalette(palette)

    # Lanza tu ventana principal
    window = LoginRegisterApp()

    def cerrar_hilos_al_salir():
        if hasattr(window, 'homeapp_admin') and hasattr(window.homeapp_admin, 'serial_thread'):
            window.homeapp_admin.serial_thread.stop()
            window.homeapp_admin.serial_thread.quit()
            window.homeapp_admin.serial_thread.wait()
            print("🛑 Hilo serial cerrado desde aboutToQuit.")
            try:
                import serial
                arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
                arduino.write(b'BAOFF\n')
                print("🚿 Bomba de agua apagada automáticamente al salir.")
                arduino.close()
            except Exception as e:
                print("⚠️ No se pudo apagar la bomba al salir:", e)

            app.aboutToQuit.connect(cerrar_hilos_al_salir)


    window.show()

    # Encender bomba de agua al iniciar
    try:
        arduino_bomba = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
        time.sleep(2)
        arduino_bomba.write(b'BAON\n')
        print("🚿 Bomba de agua encendida automáticamente.")
    except serial.SerialException as e:
        print("❌ No se pudo encender la bomba de agua automáticamente:", e)


    try:
        exit_code = app.exec_()
    finally:
        if hasattr(window, 'homeapp_admin') and hasattr(window.homeapp_admin, 'serial_thread'):
            window.homeapp_admin.serial_thread.stop()
            window.homeapp_admin.serial_thread.quit()
            window.homeapp_admin.serial_thread.wait()

    sys.exit(exit_code)