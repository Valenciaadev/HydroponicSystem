# models/hydrobox_thread.py
from collections import deque
from threading import Lock
from PyQt5.QtCore import QTimer, pyqtSignal, QThread, pyqtSlot
import time, serial, re, pytz
import RPi.GPIO as GPIO
from datetime import datetime
from time import monotonic

# Reutiliza tu función existente
from models.database import *

class HydroBoxMainThread(QThread):

    # ---- Señales públicas ----
    tx_command     = pyqtSignal(bytes)   # ← ENVÍO CENTRALIZADO DE COMANDOS (UI → hilo)
    datos_sensores = pyqtSignal(dict)
    log            = pyqtSignal(str)
    started_dose   = pyqtSignal(str)
    finished_dose  = pyqtSignal(str)
    error          = pyqtSignal(str)
    db_saved       = pyqtSignal(dict)

    def __init__(
        self,
        poolkit_port='/dev/ttyUSB0',   # ESP32 (PH/ORP/TEMP_agua)
        ambiente_port='/dev/ttyACM0',  # Arduino (TEMP_aire/HUM/nivel + bombas)
        baudrate=9600,
        trig_pin=8, echo_pin=10, altura_total=45,
        tz_name='America/Mexico_City',
        weekday=0, hour=10, minute=0,
        t_bomba1=3452, t_bomba2=3452, t_bomba3=1708,
        parent=None
    ):
        super().__init__(parent)
        # Puertos
        self.poolkit_port  = poolkit_port
        self.ambiente_port = ambiente_port
        self.baudrate      = baudrate

        # Ultrasónico
        self.trig = trig_pin
        self.echo = echo_pin
        self.altura_total = float(altura_total)

        # Dosis (scheduler)
        self._tz = pytz.timezone(tz_name)
        self.weekday = int(weekday)
        self.hour    = int(hour)
        self.minute  = int(minute)

        # ms para compatibilidad con la UI
        self.t_bomba1 = int(t_bomba1)
        self.t_bomba2 = int(t_bomba2)
        self.t_bomba3 = int(t_bomba3)
        # s internos
        self.t_b1 = self.t_bomba1 / 1000.0
        self.t_b2 = self.t_bomba2 / 1000.0
        self.t_b3 = self.t_bomba3 / 1000.0

        # Flags
        self._running = True
        self._ya_ejecuto_hoy = False
        self._manual_trigger = False

        # Serial handlers
        self.ser_pool = None    # ESP32
        self.ser_amb  = None    # Arduino

        # Cola TX para comandos UI → Arduino (sin reabrir serial)
        self.tx_queue = deque()
        self._tx_lock = Lock()          # ← acceso seguro entre hilos

        # Máquina de estados de dosificación
        self._dose_active = False
        self._dose_steps = []
        self._dose_idx = 0
        self._dose_next_ts = 0.0
        self._dose_etiqueta = ""
        self._dose_custom = None
        self._ultimo_estado_dose = "idle"

        # Cache últimos datos
        self._last = {
            "temp_agua": None, "ph": None, "orp": None,
            "temp_aire": None, "humedad_aire": None, "nivel_agua": None,
            "en_dosificacion": False, "etapa_dosis": "idle",
            "hora": None
        }

        # Guardado por franja
        self._ultima_hora_guardado = None

        # GPIO
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.trig, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.echo, GPIO.IN)

    # ---------- API pública ----------
    def detener(self):
        """
        Detiene el hilo y garantiza que se envíen los comandos pendientes (ALL_OFF/BAON, etc.)
        antes de cerrar el puerto serie.
        """
        # Prioridad: abortar dosificación y drenar TX antes de cerrar
        self._dose_active = False
        self._running = False

        # Drenaje bloqueante de la cola de TX (hasta 2 s)
        try:
            self._flush_tx_blocking(timeout=2.0, spacing=0.12)
        except Exception:
            pass

        # Limpieza GPIO y cierre del hilo
        try:
            GPIO.cleanup()
        except Exception:
            pass

        # No llamamos a quit()/exec_; nuestro run() sale por _running = False
        self.wait(1000)  # espera breve a que termine run()
        self._close_serials()

    def dosificar_ahora(self):
        self._manual_trigger = True

    def dosificar_bomba(self, pump:int, ms:int):
        if pump not in (1,2,3) or ms <= 0:
            self.error.emit(f"[DOSIS] Parámetros inválidos pump={pump} ms={ms}")
            return
        self._dose_custom = (pump, ms/1000.0)
        self.log.emit(f"[DOSIS] Petición puntual B{pump} por {ms} ms encolada.")

    def actualizar_programacion(self, weekday:int=None, hour:int=None, minute:int=None):
        if weekday is not None: self.weekday = int(weekday)
        if hour    is not None: self.hour    = int(hour)
        if minute  is not None: self.minute  = int(minute)
        self.log.emit(f"[CFG] Programación → Día {self.weekday}, {self.hour:02d}:{self.minute:02d}")

    def actualizar_tiempos(self, t1:int=None, t2:int=None, t3:int=None):
        if t1 is not None:
            self.t_bomba1 = int(t1); self.t_b1 = self.t_bomba1 / 1000.0
        if t2 is not None:
            self.t_bomba2 = int(t2); self.t_b2 = self.t_bomba2 / 1000.0
        if t3 is not None:
            self.t_bomba3 = int(t3); self.t_b3 = self.t_bomba3 / 1000.0
        self.log.emit(f"[CFG] Tiempos → B1:{self.t_b1}s B2:{self.t_b2}s B3:{self.t_b3}s")

    # ---------- RX/TX ----------
    @pyqtSlot(bytes)
    def _enqueue_tx(self, data: bytes):
        """Recibe comandos desde la UI y los encola para enviarlos por el puerto del Arduino."""
        try:
            if not isinstance(data, (bytes, bytearray)):
                data = bytes(data)
            if not data.endswith(b'\n'):
                data += b'\n'
            with self._tx_lock:
                self.tx_queue.append(data)
        except Exception as e:
            self.error.emit(f"TX enqueue error: {e}")

    def _pump_tx(self, max_per_loop=8, spacing=0.12):
        """
        Drena hasta max_per_loop comandos por iteración con pequeño espaciamiento.
        Esto permite que secuencias como ALL_OFF/BAON lleguen completas antes de detener el hilo.
        """
        if (self.ser_amb is None) or (not getattr(self.ser_amb, "is_open", False)):
            return
        sent = 0
        while sent < max_per_loop:
            with self._tx_lock:
                if not self.tx_queue:
                    break
                data = self.tx_queue.popleft()
            try:
                self.ser_amb.write(data)
                self.ser_amb.flush()
                # Opcional: log de depuración
                # self.log.emit(f"[SER][TX] {data.strip()!r}")
            except serial.SerialException as e:
                self.error.emit(f"TX error: {e}")
                self._safe_close(self.ser_amb)
                self.ser_amb = None
                # Reinsertar y salir; se reintentará cuando el puerto vuelva
                with self._tx_lock:
                    self.tx_queue.appendleft(data)
                break
            sent += 1
            # breve descanso para no saturar el micro
            time.sleep(spacing)

    def _flush_tx_blocking(self, timeout=2.0, spacing=0.12):
        """
        Envía de forma bloqueante todo lo pendiente en la cola de TX o hasta que
        expire el timeout. No depende del bucle principal.
        """
        t0 = monotonic()
        while True:
            # Si no hay puerto o ya está vacío, terminamos
            if (self.ser_amb is None) or (not getattr(self.ser_amb, "is_open", False)):
                break
            with self._tx_lock:
                empty = (len(self.tx_queue) == 0)
            if empty:
                break
            # Envía varios por ráfagas
            self._pump_tx(max_per_loop=8, spacing=spacing)
            if monotonic() - t0 > timeout:
                self.error.emit("[SER][TX] Flush timeout: quedaron comandos sin enviar.")
                break

    # ---------- Ciclo del hilo ----------
    def run(self):
        self.log.emit("[HydroBox] Hilo principal iniciado.")
        # Conectar la señal de TX a nuestro encolador (desde la UI)
        self.tx_command.connect(self._enqueue_tx)

        self._open_serials(initial=True)

        while self._running:
            try:
                self._ensure_serials()

                # Drenar TX al inicio para priorizar órdenes de usuario (apagados, etc.)
                self._pump_tx()

                # 1) Lectura PoolKit (ESP32)
                self._leer_poolkit()

                # 2) Lectura Ambiente + Nivel (Arduino)
                self._leer_ambiente_y_nivel()

                # 3) Scheduler y progreso de dosificación
                self._chequear_dosificacion()
                self._progresar_dosificacion()

                # 4) Guardado periódico
                self._guardar_si_corresponde()

                # 5) Emisión UI
                self._emit_update()

                # Drenar TX otra vez por si quedaron comandos
                self._pump_tx()

                time.sleep(0.12)  # tick suave
            except Exception as e:
                self.error.emit(f"[HydroBox] Loop error: {e}")
                time.sleep(0.3)

        # Al salir, intentar último flush breve
        try:
            self._flush_tx_blocking(timeout=0.6, spacing=0.08)
        except Exception:
            pass

        self._close_serials()
        self.log.emit("[HydroBox] Hilo principal finalizado.")

    # ---------- Serial: abrir/cerrar/asegurar ----------
    def _open_serials(self, initial=False):
        # ESP32
        try:
            if self.ser_pool is None:
                self.ser_pool = serial.Serial(self.poolkit_port, self.baudrate, timeout=0.1)
                time.sleep(2)  # ESP32 listo
                if initial: self.log.emit(f"[SER] Conectado PoolKit en {self.poolkit_port}")
        except Exception as e:
            if initial: self.error.emit(f"[SER] PoolKit no disponible: {e}")
            self.ser_pool = None

        # Arduino (sin reset por DTR/RTS)
        try:
            if self.ser_amb is None:
                self.ser_amb = serial.Serial(
                    self.ambiente_port,
                    self.baudrate,
                    timeout=0.05,
                    rtscts=False,
                    dsrdtr=False,
                )
                # Evitar reset al abrir: bajar DTR/RTS
                try:
                    self.ser_amb.setDTR(False)
                    self.ser_amb.setRTS(False)
                except Exception:
                    pass

                time.sleep(1.0)  # breve estabilización

                try:
                    self.ser_amb.reset_input_buffer()
                    # Inicialización de modo lectura continua (ajusta a tu firmware)
                    self.ser_amb.write(b"LEER\n")
                    self.ser_amb.write(b"TON\n")
                except Exception:
                    pass

                if initial: self.log.emit(f"[SER] Conectado Arduino en {self.ambiente_port}")
        except Exception as e:
            if initial: self.error.emit(f"[SER] Arduino no disponible: {e}")
            self.ser_amb = None

    def _ensure_serials(self):
        if (self.ser_pool is None) or (not getattr(self.ser_pool, "is_open", False)):
            self._safe_close(self.ser_pool); self.ser_pool = None
            self._open_serials()
        if (self.ser_amb  is None) or (not getattr(self.ser_amb, "is_open", False)):
            self._safe_close(self.ser_amb); self.ser_amb = None
            self._open_serials()

    def _close_serials(self):
        self._safe_close(self.ser_pool); self.ser_pool = None
        self._safe_close(self.ser_amb);  self.ser_amb  = None

    @staticmethod
    def _safe_close(ser):
        try:
            if ser and ser.is_open: ser.close()
        except Exception:
            pass

    # ---------- Lecturas ----------
    def _leer_poolkit(self):
        if not self.ser_pool: return
        try:
            line = self.ser_pool.readline().decode('utf-8', errors='ignore').strip()
            if not line: return
            # Formato: "TEMP:xx.x,PH:xx.xx,ORP:xxx"
            try:
                data = dict(item.split(':') for item in line.split(','))
                temp = float(data.get('TEMP', 'nan'))
                ph   = float(data.get('PH', 'nan'))
                orp  = float(data.get('ORP', 'nan'))
                if temp == temp:  self._last["temp_agua"] = temp
                if ph   == ph:    self._last["ph"]        = ph
                if orp  == orp:   self._last["orp"]       = orp
            except Exception:
                pass
        except serial.SerialException as e:
            self.error.emit(f"[SER] PoolKit lectura: {e}")
            self._safe_close(self.ser_pool); self.ser_pool = None

    def _leer_ambiente_y_nivel(self):
        # Ultrasonico
        try:
            GPIO.output(self.trig, False)
            time.sleep(0.0002)
            GPIO.output(self.trig, True)
            time.sleep(0.00001)
            GPIO.output(self.trig, False)

            start = time.time()
            timeout = start + 0.03
            while GPIO.input(self.echo) == 0 and time.time() < timeout:
                pass
            pulse_start = time.time()
            timeout2 = pulse_start + 0.03
            while GPIO.input(self.echo) == 1 and time.time() < timeout2:
                pass
            pulse_end = time.time()
            pulse = pulse_end - pulse_start
            distancia = pulse * 17150.0  # cm aprox
            if 2.0 < distancia < 400.0:
                nivel = round(self.altura_total - distancia, 2)
                self._last["nivel_agua"] = float(nivel)
        except Exception:
            pass

        # Temp/Humedad (Arduino)
        if not self.ser_amb:
            return
        t_end = time.time() + 0.15
        try:
            while time.time() < t_end:
                raw = self.ser_amb.readline().decode('utf-8', errors='ignore').strip()
                if not raw:
                    break

                U = raw.upper()

                if ("HUM" in U) or ("HUMEDAD" in U) or ("TEMP" in U) or ("TEMPERAT" in U):
                    self.log.emit(f"[SER][AMB] {raw}")

                # Combinado
                m_combo = re.search(
                    r'(?i)(?:hum\w*|humedad\w*)[^0-9\-]*([-+]?\d+(?:\.\d+)?)\s*%?.*?'
                    r'(?:temp\w*|temperatura\w*)[^0-9\-]*([-+]?\d+(?:\.\d+)?)',
                    raw
                )
                if m_combo:
                    try: self._last["humedad_aire"] = float(m_combo.group(1))
                    except Exception: pass
                    try: self._last["temp_aire"] = float(m_combo.group(2))
                    except Exception: pass
                    continue

                # Humedad sola
                m_hum = re.search(
                    r'(?i)(?:\bhum\b|humedad|hra|hrel)[^0-9\-]*[:=\s]\s*([-+]?\d+(?:\.\d+)?)\s*%?',
                    raw
                )
                if m_hum:
                    try: self._last["humedad_aire"] = float(m_hum.group(1))
                    except Exception: pass
                    continue

                # Temperatura sola
                m_temp = re.search(
                    r'(?i)(?:temp(?:_aire)?|temperatura)[^0-9\-]*[:=\s]\s*([-+]?\d+(?:\.\d+)?)',
                    raw
                )
                if m_temp:
                    try: self._last["temp_aire"] = float(m_temp.group(1))
                    except Exception: pass
                    continue

                # Último recurso
                if "HUM" in U or "HUMEDAD" in U:
                    m_any = re.search(r'([-+]?\d+(?:\.\d+)?)', raw)
                    if m_any:
                        try: self._last["humedad_aire"] = float(m_any.group(1))
                        except Exception: pass
                        continue
        except serial.SerialException as e:
            self.error.emit(f"[SER] Arduino lectura: {e}")
            self._safe_close(self.ser_amb); self.ser_amb = None

    # ---------- Dosificación ----------
    def _chequear_dosificacion(self):
        # Reset diario
        now = datetime.now(self._tz)
        if now.hour == 0 and now.minute == 0 and self._ya_ejecuto_hoy:
            self._ya_ejecuto_hoy = False
            self.log.emit("[DOSIS] Reset diario listo.")

        # Programada
        if (now.weekday() == self.weekday and now.hour == self.hour and
            now.minute == self.minute and not self._ya_ejecuto_hoy and not self._dose_active):
            self._programar_dosis_completa("programada")
            self._ya_ejecuto_hoy = True

        # Manual completa
        if self._manual_trigger and not self._dose_active:
            self._manual_trigger = False
            self._programar_dosis_completa("manual")

        # Manual puntual
        if (self._dose_custom is not None) and (not self._dose_active):
            pump, segs = self._dose_custom
            self._dose_custom = None
            self._programar_dosis_puntual(pump, segs)

    def _programar_dosis_completa(self, etiqueta:str):
        self._dose_steps = [
            ("BON1\n", self.t_b1, "B1 ON"),
            ("BOFF1\n", 0.4,      "B1 OFF"),
            ("BON2\n", self.t_b2, "B2 ON"),
            ("BOFF2\n", 0.4,      "B2 OFF"),
            ("BON3\n", self.t_b3, "B3 ON"),
            ("BOFF3\n", 0.0,      "B3 OFF"),
        ]
        self._iniciar_dose(etiqueta)

    def _programar_dosis_puntual(self, pump:int, segs:float):
        cmd_on  = f"BON{pump}\n"
        cmd_off = f"BOFF{pump}\n"
        self._dose_steps = [
            (cmd_on,  segs, f"B{pump} ON"),
            (cmd_off, 0.0,  f"B{pump} OFF"),
        ]
        self._iniciar_dose(f"puntual B{pump}")

    def _iniciar_dose(self, etiqueta:str):
        if not self.ser_amb:
            self.error.emit("[DOSIS] Arduino no disponible para dosificar.")
            return
        self._dose_active   = True
        self._dose_idx      = 0
        self._dose_next_ts  = 0.0
        self._dose_etiqueta = etiqueta
        self._ultimo_estado_dose = "start"
        stamp = datetime.now(self._tz).strftime('%Y-%m-%d %H:%M:%S')
        self.started_dose.emit(f"[{stamp}] Iniciando dosificación ({etiqueta})...")
        self.log.emit(f"[DOSIS] Secuencia ({etiqueta}) preparada.")

    def _progresar_dosificacion(self):
        self._last["en_dosificacion"] = bool(self._dose_active)
        self._last["etapa_dosis"]     = self._ultimo_estado_dose

        if not self._dose_active or not self.ser_amb:
            return

        now = monotonic()
        if self._dose_next_ts == 0.0 or now >= self._dose_next_ts:
            if self._dose_idx >= len(self._dose_steps):
                self._dose_active = False
                self._ultimo_estado_dose = "idle"
                stamp = datetime.now(self._tz).strftime('%Y-%m-%d %H:%M:%S')
                self.finished_dose.emit(f"[{stamp}] Dosificación completa ({self._dose_etiqueta}).")
                return

            cmd, wait_secs, label = self._dose_steps[self._dose_idx]
            try:
                self.ser_amb.write(cmd.encode('utf-8'))
                self._ultimo_estado_dose = label
                self.log.emit(f"[DOSIS] {label}")
            except serial.SerialException as e:
                self.error.emit(f"[DOSIS] Error serial al enviar '{cmd.strip()}': {e}")
                self._dose_active = False
                self._ultimo_estado_dose = "abort"
                return

            self._dose_next_ts = monotonic() + (wait_secs if wait_secs > 0 else 0.05)
            self._dose_idx += 1

    # ---------- Guardado ----------
    def _guardar_si_corresponde(self):
        now = datetime.now(self._tz)

        test_conf = getattr(self, '_test_guardar_cada_minuto', 0)
        if isinstance(test_conf, bool):
            interval_min = 1 if test_conf else 0
        elif isinstance(test_conf, (int, float)) and test_conf > 0:
            interval_min = int(test_conf)
        else:
            interval_min = 0

        if interval_min > 0:
            last_ts = getattr(self, '_ultimo_save_ts_test', None)
            if last_ts and (now - last_ts).total_seconds() < 60 * interval_min:
                return
        else:
            if now.minute != 0:
                return
            slot = (now.date(), now.hour)
            if getattr(self, '_ultima_slot_guardado', None) == slot:
                return

        ph         = self._last.get("ph")
        orp        = self._last.get("orp")
        temp_agua  = self._last.get("temp_agua")
        nivel      = self._last.get("nivel_agua")
        temp_aire  = self._last.get("temp_aire")
        hum        = self._last.get("humedad_aire")

        if all(v is None for v in (ph, orp, temp_agua, nivel, temp_aire, hum)):
            self.log.emit("[DB] No hay datos para guardar en este momento.")
            if interval_min > 0:
                setattr(self, '_ultimo_save_ts_test', now)
            else:
                setattr(self, '_ultima_slot_guardado', (now.date(), now.hour))
            return

        try:
            self.log.emit(f"[DB][Preview] ph={ph}, orp={orp}, tAgua={temp_agua}, nivel={nivel}, tAire={temp_aire}, hum={hum}")
            guardar_mediciones_cada_6h(
                ph=ph,
                orp=orp,
                temp_agua=temp_agua,
                nivel_agua=nivel,
                temp_aire=temp_aire,
                humedad_aire=hum
            )
            payload = {
                "fecha": now.strftime('%Y-%m-%d %H:%M:%S'),
                "ph": ph, "orp": orp, "temp_agua": temp_agua,
                "nivel_agua": nivel, "temp_aire": temp_aire, "humedad_aire": hum
            }
            self.db_saved.emit(payload)

            if interval_min > 0:
                setattr(self, '_ultimo_save_ts_test', now)
                self.log.emit(f"[DB] Guardado OK (cada {interval_min} min @ {now.hour:02d}:{now.minute:02d}).")
            else:
                setattr(self, '_ultima_slot_guardado', (now.date(), now.hour))
                self.log.emit(f"[DB] Guardado OK (cada hora {now.hour:02d}:00).")
        except Exception as e:
            self.error.emit(f"[DB] Error al guardar: {e}")

    # ---------- Emisión consolidada ----------
    def _emit_update(self):
        self._last["hora"] = datetime.now(self._tz).strftime("%d/%m %H:%M:%S")
        self.datos_sensores.emit(dict(self._last))
