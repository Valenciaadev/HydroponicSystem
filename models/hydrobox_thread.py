# models/hydrobox_thread.py
from PyQt5.QtCore import QThread, pyqtSignal
import time, serial, re, pytz
import RPi.GPIO as GPIO
from datetime import datetime
from time import monotonic

# Reutiliza tu función existente
from models.database import *

class HydroBoxMainThread(QThread):
    # Unificamos señales
    datos_sensores = pyqtSignal(dict)  # payload con todo
    log            = pyqtSignal(str)
    started_dose   = pyqtSignal(str)
    finished_dose  = pyqtSignal(str)
    error          = pyqtSignal(str)

    def __init__(
        self,
        poolkit_port='/dev/ttyUSB0',   # ESP32 (PH/ORP/TEMP_agua)
        ambiente_port='/dev/ttyACM0',  # Arduino (TEMP_aire/HUM/nivel + bombas)
        baudrate=9600,
        trig_pin=8, echo_pin=10, altura_total=45,
        tz_name='America/Mexico_City',
        weekday=0, hour=10, minute=0,          # programación por defecto
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

        # ms para compatibilidad con la UI (ActuatorManagmentWidget._ms_por_ml usa t_bomba1/2/3)
        self.t_bomba1 = int(t_bomba1)
        self.t_bomba2 = int(t_bomba2)
        self.t_bomba3 = int(t_bomba3)

        # segundos para la lógica interna del hilo (secuencia de dosificación)
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

        # Máquina de estados NO bloqueante para dosificación
        self._dose_active = False
        self._dose_steps = []         # lista de pasos
        self._dose_idx = 0
        self._dose_next_ts = 0.0
        self._dose_etiqueta = ""
        self._dose_custom = None      # (pump, segs) si es puntual
        self._ultimo_estado_dose = "idle"

        # Cache de últimos datos para emisión consolidada
        self._last = {
            "temp_agua": None, "ph": None, "orp": None,
            "temp_aire": None, "humedad_aire": None, "nivel_agua": None,
            "en_dosificacion": False, "etapa_dosis": "idle",
            "hora": None
        }

        # Guardados por franja (independientes)
        self._ultima_hora_guardado_pool = None
        self._ultima_hora_guardado_amb  = None

        # GPIO init
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.trig, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.echo, GPIO.IN)

    # ---------- API pública ----------
    def detener(self):
        self._running = False
        self.quit()
        self.wait()
        try:
            GPIO.cleanup()
        except Exception:
            pass
        self._close_serials()

    def dosificar_ahora(self):
        self._manual_trigger = True

    def dosificar_bomba(self, pump:int, ms:int):
        # programa una dosificación puntual NO bloqueante
        if pump not in (1,2,3) or ms <= 0:
            self.error.emit(f"[DOSIS] Parámetros inválidos pump={pump} ms={ms}")
            return
        # Si ya hay una dosificación activa, la ponemos en cola simple (cuando termine)
        self._dose_custom = (pump, ms/1000.0)
        self.log.emit(f"[DOSIS] Petición puntual B{pump} por {ms} ms encolada.")

    def actualizar_programacion(self, weekday:int=None, hour:int=None, minute:int=None):
        if weekday is not None: self.weekday = int(weekday)
        if hour    is not None: self.hour    = int(hour)
        if minute  is not None: self.minute  = int(minute)
        self.log.emit(f"[CFG] Programación → Día {self.weekday}, {self.hour:02d}:{self.minute:02d}")

    def actualizar_tiempos(self, t1:int=None, t2:int=None, t3:int=None):
        if t1 is not None:
            self.t_bomba1 = int(t1)
            self.t_b1 = self.t_bomba1 / 1000.0
        if t2 is not None:
            self.t_bomba2 = int(t2)
            self.t_b2 = self.t_bomba2 / 1000.0
        if t3 is not None:
            self.t_bomba3 = int(t3)
            self.t_b3 = self.t_bomba3 / 1000.0
        self.log.emit(f"[CFG] Tiempos → B1:{self.t_b1}s B2:{self.t_b2}s B3:{self.t_b3}s")

    # ---------- Ciclo del hilo ----------
    def run(self):
        self.log.emit("[HydroBox] Hilo principal iniciado.")
        self._open_serials(initial=True)

        while self._running:
            try:
                self._ensure_serials()

                # 1) Lectura PoolKit (ESP32)
                self._leer_poolkit()

                # 2) Lectura Ambiente + Nivel (Arduino)
                self._leer_ambiente_y_nivel()

                # 3) Scheduler y progreso de dosificación (NO bloqueante)
                self._chequear_dosificacion()
                self._progresar_dosificacion()

                # 4) Guardado cada 6h
                self._guardar_si_corresponde()

                # 5) Emitir a UI (consolidado)
                self._emit_update()

                time.sleep(0.15)  # tick corto y suave
            except Exception as e:
                self.error.emit(f"[HydroBox] Loop error: {e}")
                time.sleep(0.5)

        self._close_serials()
        self.log.emit("[HydroBox] Hilo principal finalizado.")

    # ---------- Serial: abrir/cerrar/asegurar ----------
    def _open_serials(self, initial=False):
        try:
            if self.ser_pool is None:
                self.ser_pool = serial.Serial(self.poolkit_port, self.baudrate, timeout=0.1)
                time.sleep(2)  # ESP32 listo
                if initial: self.log.emit(f"[SER] Conectado PoolKit en {self.poolkit_port}")
        except Exception as e:
            if initial: self.error.emit(f"[SER] PoolKit no disponible: {e}")
            self.ser_pool = None

        try:
            if self.ser_amb is None:
                self.ser_amb = serial.Serial(self.ambiente_port, self.baudrate, timeout=0.05)
                time.sleep(2)  # Arduino puede resetear al abrir
                # Inicializar modo lectura continua en Arduino (como hacías)
                try:
                    self.ser_amb.reset_input_buffer()
                    self.ser_amb.write(b"LEER\r\n")
                    self.ser_amb.write(b"TON\r\n")
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
            # Esperamos formato: "TEMP:xx.x,PH:xx.xx,ORP:xxx"
            try:
                data = dict(item.split(':') for item in line.split(','))
                temp = float(data.get('TEMP', 'nan'))
                ph   = float(data.get('PH', 'nan'))
                orp  = float(data.get('ORP', 'nan'))
                if temp == temp:  self._last["temp_agua"] = temp
                if ph   == ph:    self._last["ph"]        = ph
                if orp  == orp:   self._last["orp"]       = orp
            except Exception:
                # Línea no válida pero no rompemos el hilo
                pass
        except serial.SerialException as e:
            self.error.emit(f"[SER] PoolKit lectura: {e}")
            self._safe_close(self.ser_pool); self.ser_pool = None

    def _leer_ambiente_y_nivel(self):
        # 2.1 Ultrasónico (igual que ya tienes)
        try:
            GPIO.output(self.trig, False)
            time.sleep(0.0002)
            GPIO.output(self.trig, True)
            time.sleep(0.00001)
            GPIO.output(self.trig, False)

            start = time.time()
            timeout = start + 0.03  # 30 ms
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

        # 2.2 Temp/Humedad por serial (Arduino) — parseo robusto
        if not self.ser_amb:
            return
        t_end = time.time() + 0.15
        try:
            while time.time() < t_end:
                raw = self.ser_amb.readline().decode('utf-8', errors='ignore').strip()
                if not raw:
                    break

                U = raw.upper()

                # 👉 Log de depuración solo si la línea menciona HUM o TEMP
                if ("HUM" in U) or ("HUMEDAD" in U) or ("TEMP" in U) or ("TEMPERAT" in U):
                    self.log.emit(f"[SER][AMB] {raw}")

                # 1) Línea combinada: "Humidity: 55.0% ... Temp: 23.4C"
                m_combo = re.search(
                    r'(?i)(?:hum\w*|humedad\w*)[^0-9\-]*([-+]?\d+(?:\.\d+)?)\s*%?.*?'
                    r'(?:temp\w*|temperatura\w*)[^0-9\-]*([-+]?\d+(?:\.\d+)?)',
                    raw
                )
                if m_combo:
                    try:
                        self._last["humedad_aire"] = float(m_combo.group(1))
                    except Exception:
                        pass
                    try:
                        self._last["temp_aire"] = float(m_combo.group(2))
                    except Exception:
                        pass
                    continue

                # 2) Humedad sola (acepta HUM/HUMEDAD/HRA/HREL con o sin %, con separadores : o = o espacio)
                m_hum = re.search(
                    r'(?i)(?:\bhum\b|humedad|hra|hrel)[^0-9\-]*[:=\s]\s*([-+]?\d+(?:\.\d+)?)\s*%?',
                    raw
                )
                if m_hum:
                    try:
                        self._last["humedad_aire"] = float(m_hum.group(1))
                    except Exception:
                        pass
                    continue

                # 3) Temperatura sola (TEMP/TEMPERATURA/T_AIRE)
                m_temp = re.search(
                    r'(?i)(?:temp(?:_aire)?|temperatura)[^0-9\-]*[:=\s]\s*([-+]?\d+(?:\.\d+)?)',
                    raw
                )
                if m_temp:
                    try:
                        self._last["temp_aire"] = float(m_temp.group(1))
                    except Exception:
                        pass
                    continue

                # 4) Último recurso: cualquier "HUM" con número en la línea
                if "HUM" in U or "HUMEDAD" in U:
                    m_any = re.search(r'([-+]?\d+(?:\.\d+)?)', raw)
                    if m_any:
                        try:
                            self._last["humedad_aire"] = float(m_any.group(1))
                        except Exception:
                            pass
                        continue

                # Resto de líneas (acks/comandos) se ignoran
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

        # Manual puntual (una bomba)
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
        # Si no hay “próximo” programado, ejecuta el step actual
        if self._dose_next_ts == 0.0 or now >= self._dose_next_ts:
            if self._dose_idx >= len(self._dose_steps):
                # Terminado
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
                # abortamos la secuencia
                self._dose_active = False
                self._ultimo_estado_dose = "abort"
                return

            self._dose_next_ts = monotonic() + (wait_secs if wait_secs > 0 else 0.05)
            self._dose_idx += 1

    # ---------- Guardado 6h ----------
    def _guardar_si_corresponde(self):
        now = datetime.now(self._tz)
        if now.minute != 0:  # sólo al minuto 00
            return

        # 0, 6, 12, 18
        if now.hour not in (0,6,12,18):
            return

        # PoolKit
        if self._ultima_hora_guardado_pool != now.hour and (
            self._last["ph"] is not None or
            self._last["orp"] is not None or
            self._last["temp_agua"] is not None
        ):
            try:
                # Conservamos tu firma previa: (ph, orp, temp_agua)
                guardar_mediciones_cada_6h(self._last["ph"], self._last["orp"], self._last["temp_agua"])
                self._ultima_hora_guardado_pool = now.hour
                self.log.emit("[DB] Guardado 6h PoolKit OK.")
            except Exception as e:
                self.error.emit(f"[DB] PoolKit: {e}")

        # Ambiente
        if self._ultima_hora_guardado_amb != now.hour and (
            self._last["temp_aire"] is not None or
            self._last["humedad_aire"] is not None or
            self._last["nivel_agua"] is not None
        ):
            try:
                # Conservamos tu firma previa: (temp_aire, hum_aire, nivel_agua)
                guardar_mediciones_cada_6h(self._last["temp_aire"], self._last["humedad_aire"], self._last["nivel_agua"])
                self._ultima_hora_guardado_amb = now.hour
                self.log.emit("[DB] Guardado 6h Ambiente OK.")
            except Exception as e:
                self.error.emit(f"[DB] Ambiente: {e}")

    # ---------- Emisión consolidada ----------
    def _emit_update(self):
        self._last["hora"] = datetime.now(self._tz).strftime("%d/%m %H:%M:%S")
        self.datos_sensores.emit(dict(self._last))