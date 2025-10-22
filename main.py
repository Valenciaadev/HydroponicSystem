import sys
import time
import atexit
import signal
import serial
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QStackedWidget, QWidget, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt, QPoint, QSize, QTimer, pyqtSignal
from PyQt5.QtGui import QPalette, QColor, QIcon

# Modelos y vistas
from models.usuario import Usuario
from models.trabajador import Trabajador
from models.administrador import Administrador
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
from models.hydrobox_thread import HydroBoxMainThread

SERIAL_PORT = '/dev/ttyACM0'
SERIAL_BAUD = 9600
BOMBA_LIKE = "%Bomba de Agua%"
ACTIVE_LOW_BOMBA = True

_app_closing_flag = False  # evita limpieza duplicada

def _bomba_serial_cmd(encender: bool) -> bytes:
    if ACTIVE_LOW_BOMBA:
        return b'BAOFF' if encender else b'BAON'
    else:
        return b'BAON' if encender else b'BAOFF'

def _db_get_estado_actuador(nombre_like: str):
    """Devuelve 1, 0 o None si no se pudo leer."""
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT estado_actual FROM actuadores WHERE nombre LIKE %s LIMIT 1", (nombre_like,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row is None:
            return None
        return int(row[0]) if row[0] is not None else None
    except Exception as e:
        print("⚠️ _db_get_estado_actuador:", e)
        return None

def _db_set_estado_actuador(nombre_like: str, estado: int):
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("UPDATE actuadores SET estado_actual = %s WHERE nombre LIKE %s", (estado, nombre_like))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("⚠️ _db_set_estado_actuador:", e)
        return False

def _db_set_todos_apagados():
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("UPDATE actuadores SET estado_actual = 0")
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("⚠️ _db_set_todos_apagados:", e)
        return False

# --- Fallback legado (solo si NO hay hilo): abre/cierra serial de forma segura (sin reset) ---
def _serial_send_many(commands):
    try:
        ser = serial.Serial(
            SERIAL_PORT, SERIAL_BAUD, timeout=1,
            rtscts=False, dsrdtr=False
        )
        try:
            # Evitar reset por DTR/RTS
            try:
                ser.setDTR(False)
                ser.setRTS(False)
            except Exception:
                pass
            time.sleep(0.3)  # breve estabilización
            for cmd in commands:
                data = cmd.encode('utf-8') if isinstance(cmd, str) else cmd
                if not data.endswith(b'\n'):
                    data += b'\n'
                ser.write(data)
                ser.flush()
                time.sleep(0.08)  # pequeño espaciamiento
        finally:
            ser.close()
        return True
    except Exception as e:
        print("⚠️ _serial_send_many:", e)
        return False

# Helper central para TX (prioriza el hilo; si no hay, usa serial directo)
def send_cmd(cmd):
    # cmd puede ser str o bytes
    try:
        ht = getattr(window, 'hydro_thread', None)
    except NameError:
        ht = None
    data = cmd.encode('utf-8') if isinstance(cmd, str) else cmd
    if ht and hasattr(ht, 'tx_command') and ht.isRunning():
        ht.tx_command.emit(data)
        return True
    else:
        # Fallback: serial directo
        return _serial_send_many([data])

def encender_bomba_agua_seguro():
    estado = _db_get_estado_actuador(BOMBA_LIKE)
    if estado == 1:
        print("ℹ️ Bomba ya estaba encendida.")
        return False
    ok_serial = send_cmd(_bomba_serial_cmd(True))
    if ok_serial:
        _db_set_estado_actuador(BOMBA_LIKE, 1)  # DB = encendida
        print("✅ Bomba encendida (arranque).")
        return True
    print("❌ No se pudo encender la bomba por serial.")
    return False

def apagar_bomba_agua_seguro(motivo="salida", sync=False):
    estado = _db_get_estado_actuador(BOMBA_LIKE)
    if estado == 0:
        print(f"ℹ️ Bomba ya estaba apagada ({motivo}).")
        return False

    try:
        ht = getattr(window, 'hydro_thread', None)
    except NameError:
        ht = None

    cmd_off = _bomba_serial_cmd(False)
    ok_serial = False

    if sync and ht and hasattr(ht, 'tx_command') and ht.isRunning():
        # Enviar directo al hilo y esperar a que lo drene
        ht.tx_command.emit(cmd_off)
        time.sleep(0.25)  # darle tiempo a _pump_tx
        ok_serial = True
    elif sync:
        # Sin hilo: manda por serial directo (bloqueante)
        ok_serial = _serial_send_many([cmd_off])
    else:
        ok_serial = send_cmd(cmd_off)

    if ok_serial:
        _db_set_estado_actuador(BOMBA_LIKE, 0)  # DB = apagada
        print(f"✅ Bomba apagada ({motivo}).")
        return True
    print("❌ No se pudo apagar la bomba por serial.")
    return False

def apagar_todos_actuadores_seguro(motivo="salida", sync=False):
    cmds = [
        b'ALL_OFF',   # si tu firmware lo soporta
        b'LAMPOFF', b'FANOFF',
        b'B1OFF', b'B2OFF', b'B3OFF',
        _bomba_serial_cmd(False),  # ← BOMBA APAGADA físico
    ]

    try:
        ht = getattr(window, 'hydro_thread', None)
    except NameError:
        ht = None

    serial_ok = True

    if sync:
        if ht and hasattr(ht, 'tx_command') and ht.isRunning():
            # Enviar por el hilo, pero BLOQUEANTE (sin QTimer)
            for c in cmds:
                ht.tx_command.emit(c)
                time.sleep(0.15)  # coincide con espaciamiento del hilo
        else:
            # Sin hilo: manda por serial directo (bloqueante)
            serial_ok = _serial_send_many(cmds)
    else:
        # Camino normal en ejecución (UI viva): programar con pequeños retardos
        for i, c in enumerate(cmds):
            QTimer.singleShot(120 * i, lambda cc=c: send_cmd(cc))

    ok_db = _db_set_todos_apagados()
    if ok_db:
        print("✅ Estados de actuadores = 0 en DB.")
    else:
        print("⚠️ No se pudo actualizar la DB al apagar todos.")

    return serial_ok and ok_db

# ===== Helper para cablear señales de sensores a CUANTOS widgets existan =====
def _wire_sensor_consumers(app_obj, homeapp):
    """
    Conecta hydro_thread.datos_sensores a:
      - homeapp.inicio_widget (si existe)
      - homeapp.summary_widget (si existe)
      - cualquier atributo del homeapp que tenga 'recibir_datos_sensores'
    Esto asegura que Temp/Humedad de aire lleguen a las cartas del Summary.
    """
    ht = getattr(app_obj, 'hydro_thread', None)
    if not ht:
        return

    def _try_connect(target):
        if target and hasattr(target, 'recibir_datos_sensores'):
            try:
                ht.datos_sensores.connect(target.recibir_datos_sensores)
            except Exception:
                pass

    posibles = []
    posibles.append(getattr(homeapp, 'inicio_widget', None))
    posibles.append(getattr(homeapp, 'summary_widget', None))
    # Escanea atributos comunes del contenedor por si cambian nombres:
    for name in dir(homeapp):
        if name.endswith('_widget') and name not in ('inicio_widget', 'summary_widget'):
            posibles.append(getattr(homeapp, name, None))

    for w in posibles:
        _try_connect(w)

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
    hydro_ready = pyqtSignal(object) 
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sistema Hidropónico")
        self.setGeometry(660, 200, 500, 500)
        self.setStyleSheet("background-color: #1E1B2E;")
        self.setWindowFlags(Qt.FramelessWindowHint)

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
        self.stack.setCurrentWidget(self.user_select_widget)

        self.hydro_thread = None

    def _start_hydro_if_needed(self):
        """Arranca el hilo una sola vez y cablea señales al/los widgets existentes."""
        if (self.hydro_thread is None) or (not self.hydro_thread.isRunning()):
            self.hydro_thread = HydroBoxMainThread(
                poolkit_port='/dev/ttyUSB0',     # ESP32 (TEMP_agua/PH/ORP)
                ambiente_port=SERIAL_PORT,       # Arduino (TEMP_aire/HUM/Nivel + bombas)
                baudrate=SERIAL_BAUD,
                trig_pin=8, echo_pin=10, altura_total=45,
                tz_name='America/Mexico_City',
                weekday=0, hour=10, minute=0,
                t_bomba1=3452, t_bomba2=3452, t_bomba3=1708,
                parent=self
            )
            # Logs y eventos
            self.hydro_thread.log.connect(lambda m: print(m))
            self.hydro_thread.error.connect(lambda m: print("ERR:", m))
            self.hydro_thread.started_dose.connect(lambda m: print(m))
            self.hydro_thread.finished_dose.connect(lambda m: print(m))
            # Arranca
            self.hydro_thread.start()
            self.hydro_ready.emit(self.hydro_thread)
            # Demo: guarda cada minuto para que el Summary vea datos recientes
            self.hydro_thread._test_guardar_cada_minuto = 1

        # Si ya existen vistas Home, conecta ahora a sus consumidores
        if hasattr(self, 'homeapp_admin'):
            _wire_sensor_consumers(self, self.homeapp_admin)
        if hasattr(self, 'homeapp_worker'):
            _wire_sensor_consumers(self, self.homeapp_worker)

    def mostrar_panel_admin(self):
        if hasattr(self, 'homeapp_admin'):
            if hasattr(self.homeapp_admin, 'inicio_widget') and hasattr(self.homeapp_admin.inicio_widget, 'liberar_camara'):
                self.homeapp_admin.inicio_widget.liberar_camara()
            self.homeapp_admin.close()
            del self.homeapp_admin

        self.homeapp_admin = HomeappAdmin(self)
        # Asegura hilo y conecta sensores a todos los widgets relevantes
        self._start_hydro_if_needed()
        _wire_sensor_consumers(self, self.homeapp_admin)

        self.homeapp_admin.showFullScreen()
        self.hide()

    def mostrar_panel_worker(self):
        if hasattr(self, 'homeapp_worker'):
            if hasattr(self.homeapp_worker, 'inicio_widget') and hasattr(self.homeapp_worker.inicio_widget, 'liberar_camara'):
                self.homeapp_worker.inicio_widget.liberar_camara()
            self.homeapp_worker.close()
            del self.homeapp_worker

        self.homeapp_worker = HomeappWorker(self)
        # Asegura hilo y conecta sensores a todos los widgets relevantes
        self._start_hydro_if_needed()
        _wire_sensor_consumers(self, self.homeapp_worker)

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
        try:
            # 🔴 Apaga en modo bloqueante (estamos cambiando de vista)
            apagar_todos_actuadores_seguro(motivo="cerrar_sesion", sync=True)
        except Exception as e:
            print("⚠️ Error apagando al cerrar sesión:", e)

        try:
            if hasattr(self, "hydro_thread") and self.hydro_thread is not None:
                self.hydro_thread.detener()
        except Exception as e:
            print("⚠️ No se pudo detener HydroBoxMainThread al cerrar sesión:", e)

        self.stack.setCurrentWidget(self.user_select_widget)

def _encendido_inicial_bomba():
    try:
        encender_bomba_agua_seguro()
    except Exception as e:
        print("❌ Error en encendido inicial de bomba:", e)

def _cierre_ordenado(window: LoginRegisterApp, motivo="aboutToQuit/atexit/signal"):
    global _app_closing_flag
    if _app_closing_flag:
        return
    _app_closing_flag = True

    print(f"🔻 Cierre ordenado invocado ({motivo})")

    try:
        # 1) Apagar TODO de forma BLOQUEANTE para asegurar OFF aunque el loop muera
        apagar_todos_actuadores_seguro(motivo=motivo, sync=True)
        # 2) Si el hilo existe, darle un respiro para drenar TX y luego detener
        if hasattr(window, "hydro_thread") and window.hydro_thread is not None and window.hydro_thread.isRunning():
            time.sleep(0.3)
            window.hydro_thread.detener()
    except Exception as e:
        print("⚠️ Problema durante cierre ordenado:", e)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#1E1B2E"))
    palette.setColor(QPalette.WindowText, QColor("#FFFFFF"))
    app.setPalette(palette)

    window = LoginRegisterApp()
    window.show()

    # Enciende la bomba 3 s después (evita golpear al sistema durante el arranque gráfico)
    QTimer.singleShot(3000, _encendido_inicial_bomba)

    # Opcional: arranca el hilo YA para que Temp/Humedad lleguen al Summary aunque
    # aún no entres a Admin/Worker (si prefieres, comenta esta línea).
    window._start_hydro_if_needed()

    def _on_about_to_quit():
        _cierre_ordenado(window, motivo="aboutToQuit")

    app.aboutToQuit.connect(_on_about_to_quit)
    atexit.register(lambda: _cierre_ordenado(window, motivo="atexit"))

    try:
        signal.signal(signal.SIGINT, lambda s, f: _cierre_ordenado(window, motivo="SIGINT"))
        signal.signal(signal.SIGTERM, lambda s, f: _cierre_ordenado(window, motivo="SIGTERM"))
    except Exception:
        pass

    try:
        exit_code = app.exec_()
    finally:
        try:
            _cierre_ordenado(window, motivo="finally")
        except Exception:
            pass

    sys.exit(exit_code)

