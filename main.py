import sys
import mysql.connector
from models.usuario import Usuario
from models.trabajador import Trabajador
from models.administrador import Administrador
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QStackedWidget, QWidget, QHBoxLayout, QPushButton, QLabel, QInputDialog, QLineEdit, QMessageBox
from PyQt5.QtCore import Qt, QPoint, QSize, QTimer
from PyQt5.QtGui import QPalette, QColor, QIcon
from views.registro import RegistroWidget
from views.inicio_sesion_worker import InicioSesionWidget
from views.seleccion_usuario import SeleccionUsuarioWidget
from views.inicio_sesion_admin import InicioSesionAdministradorWidget
from controllers.auth_controller import hash_password
from views.homeapp_admin import HomeappAdmin
from views.homeapp_worker import HomeappWorker
from views.summaryapp_admin import SummaryAppAdmin
from views.summaryapp_worker import SummaryAppWorker
from models.database import connect_db

# ✅ NUEVO hilo unificado
from models.hydrobox_thread import HydroBoxMainThread

import serial
import time


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

        # Mostrar la vista de selección de usuario por defecto
        self.stack.setCurrentWidget(self.user_select_widget)

        # Referencia al hilo unificado (se crea al entrar a Admin/Worker)
        self.hydro_thread = None
        
    def mostrar_panel_admin(self):
        # Cierra instancia previa si existe
        if hasattr(self, 'homeapp_admin'):
            if hasattr(self.homeapp_admin, 'inicio_widget') and hasattr(self.homeapp_admin.inicio_widget, 'liberar_camara'):
                self.homeapp_admin.inicio_widget.liberar_camara()
            self.homeapp_admin.close()
            del self.homeapp_admin
        
        self.homeapp_admin = HomeappAdmin(self)

        # ✅ Crear e iniciar el hilo unificado solo una vez
        if (self.hydro_thread is None) or (not self.hydro_thread.isRunning()):
            self.hydro_thread = HydroBoxMainThread(
                poolkit_port='/dev/ttyUSB0',     # ESP32 (TEMP_agua/PH/ORP)
                ambiente_port='/dev/ttyACM0',    # Arduino (TEMP_aire/HUM/Nivel + bombas)
                baudrate=9600,
                trig_pin=8, echo_pin=10, altura_total=45,
                tz_name='America/Mexico_City',
                weekday=0, hour=10, minute=0,
                t_bomba1=3452, t_bomba2=3452, t_bomba3=1708,
                parent=self
            )
            # Conectar señales a la UI (vista inicio)
            iw = self.homeapp_admin.inicio_widget
            self.hydro_thread.datos_sensores.connect(iw.recibir_datos_sensores)
            # Logs (opcionalmente podrías mostrarlos en una consola)
            self.hydro_thread.log.connect(lambda m: print(m))
            self.hydro_thread.started_dose.connect(lambda m: print(m))
            self.hydro_thread.finished_dose.connect(lambda m: print(m))
            self.hydro_thread.error.connect(lambda m: print(m))
            self.hydro_thread.start()

        self.homeapp_admin.showFullScreen()
        self.hide()
    
    def mostrar_panel_worker(self):
        # Cierra instancia previa si existe
        if hasattr(self, 'homeapp_worker'):
            if hasattr(self.homeapp_worker, 'inicio_widget') and hasattr(self.homeapp_worker.inicio_widget, 'liberar_camara'):
                self.homeapp_worker.inicio_widget.liberar_camara()
            self.homeapp_worker.close()
            del self.homeapp_worker

        self.homeapp_worker = HomeappWorker(self)

        # ✅ Reusar el mismo hilo unificado (o crearlo si no está)
        if (self.hydro_thread is None) or (not self.hydro_thread.isRunning()):
            self.hydro_thread = HydroBoxMainThread(
                poolkit_port='/dev/ttyUSB0',
                ambiente_port='/dev/ttyACM0',
                baudrate=9600,
                trig_pin=8, echo_pin=10, altura_total=45,
                tz_name='America/Mexico_City',
                weekday=0, hour=10, minute=0,
                t_bomba1=3452, t_bomba2=3452, t_bomba3=1708,
                parent=self
            )
            iw = self.homeapp_worker.inicio_widget
            self.hydro_thread.datos_sensores.connect(iw.recibir_datos_sensores)
            self.hydro_thread.log.connect(lambda m: print(m))
            self.hydro_thread.started_dose.connect(lambda m: print(m))
            self.hydro_thread.finished_dose.connect(lambda m: print(m))
            self.hydro_thread.error.connect(lambda m: print(m))
            self.hydro_thread.start()
        else:
            # Si ya estaba corriendo, conectar la vista worker
            iw = self.homeapp_worker.inicio_widget
            self.hydro_thread.datos_sensores.connect(iw.recibir_datos_sensores)

        self.homeapp_worker.showFullScreen()
        self.hide()

    def switch_to_register(self):
        self.stack.setCurrentWidget(self.register_widget)

    def switch_to_login(self):
        self.stack.setCurrentWidget(self.login_widget)
    
    def switch_to_admin(self):
        self.stack.setCurrentWidget(self.login_admin_widget)

    def switch_to_worker(self): 
        self.stack.setCurrentWidget(self.login_widget)
    
    def switch_to_user_selection(self):
        self.stack.setCurrentWidget(self.user_select_widget)


def _encender_bomba_agua_al_iniciar():
    """
    Mantenemos el encendido de la bomba general (BAON) en el arranque.
    Se abre el puerto, se envía, y se cierra ANTES de iniciar HydroBoxMainThread
    para evitar contención del puerto /dev/ttyACM0.
    """
    try:
        arduino_bomba = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
        time.sleep(2)
        arduino_bomba.write(b'BAON\n')
        arduino_bomba.close()

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE actuadores SET estado_actual = 1 WHERE nombre LIKE '%Bomba de Agua%'")
            conn.commit()
            conn.close()
        except Exception as e:
            print("⚠️ Error al actualizar el estado de la bomba en la base de datos:", e)
    except serial.SerialException as e:
        print("❌ No se pudo encender la bomba de agua automáticamente:", e)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Tema oscuro
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#1E1B2E"))
    palette.setColor(QPalette.WindowText, QColor("#FFFFFF"))
    app.setPalette(palette)

    window = LoginRegisterApp()
    window.show()

    # 🚿 Encender bomba general al iniciar (antes de levantar el hilo unificado)
    _encender_bomba_agua_al_iniciar()

    # Cierre ordenado
    def cerrar_hilos_al_salir():
        try:
            if hasattr(window, "hydro_thread") and window.hydro_thread is not None:
                # Detener hilo (cierra seriales y hace GPIO.cleanup internamente)
                window.hydro_thread.detener()
        except Exception as e:
            print("⚠️ No se pudo detener HydroBoxMainThread:", e)

        # Apagar bomba general al salir
        try:
            arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
            time.sleep(1)
            arduino.write(b'BAOFF\n')
            arduino.close()
        except Exception as e:
            print("⚠️ No se pudo apagar la bomba al salir:", e)

    app.aboutToQuit.connect(cerrar_hilos_al_salir)

    try:
        exit_code = app.exec_()
    finally:
        # Redundancia segura
        try:
            if hasattr(window, "hydro_thread") and window.hydro_thread is not None:
                window.hydro_thread.detener()
        except Exception:
            pass

    sys.exit(exit_code)
