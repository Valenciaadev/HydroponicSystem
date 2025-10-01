# models/dosificador_thread.py
import time
from datetime import datetime
import pytz
from PyQt5.QtCore import QThread, pyqtSignal

import serial

class DosificadorThread(QThread):
    # Señales para que tu UI muestre logs o estados
    log = pyqtSignal(str)
    started_dose = pyqtSignal(str)     # mensaje inicio
    finished_dose = pyqtSignal(str)    # mensaje fin
    error = pyqtSignal(str)

    def __init__(
        self,
        port:str = "/dev/ttyACM0",
        baud:int = 9600,
        tz_name:str = "America/Mexico_City",
        # Programación (10:00 lunes por default)
        weekday:int = 0,    # 0=lunes ... 6=domingo
        hour:int = 10,
        minute:int = 0,
        # Tiempos en ms (tus valores actuales)
        t_bomba1:int = 3452,  # FloraMicro 8.3 ml
        t_bomba2:int = 3452,  # FloraGro   8.3 ml
        t_bomba3:int = 1708,  # FloraBloom 4.1 ml
        parent=None
    ):
        super().__init__(parent)
        self._running = True
        self._port = port
        self._baud = baud
        self._tz = pytz.timezone(tz_name)

        self.weekday = weekday
        self.hour = hour
        self.minute = minute

        self.t_bomba1 = t_bomba1
        self.t_bomba2 = t_bomba2
        self.t_bomba3 = t_bomba3

        self._ya_ejecuto_hoy = False
        self._manual_trigger = False

    # ---- API pública para UI ----
    def detener(self):
        self._running = False

    def dosificar_ahora(self):
        """Permite disparar la dosificación manual desde la interfaz."""
        self._manual_trigger = True

    def actualizar_programacion(self, weekday:int=None, hour:int=None, minute:int=None):
        if weekday is not None: self.weekday = weekday
        if hour is not None: self.hour = hour
        if minute is not None: self.minute = minute
        self.log.emit(f"[CFG] Programación actualizada → día {self.weekday}, {self.hour:02d}:{self.minute:02d}")

    def actualizar_tiempos(self, t1:int=None, t2:int=None, t3:int=None):
        if t1 is not None: self.t_bomba1 = t1
        if t2 is not None: self.t_bomba2 = t2
        if t3 is not None: self.t_bomba3 = t3
        self.log.emit(f"[CFG] Tiempos actualizados → B1:{self.t_bomba1}ms B2:{self.t_bomba2}ms B3:{self.t_bomba3}ms")

    # ---- Lógica principal ----
    def run(self):
        self.log.emit("[DOSIS] Hilo de dosificación iniciado.")
        while self._running:
            try:
                now = datetime.now(self._tz)
                dow = now.weekday()
                hh = now.hour
                mm = now.minute

                # Reset diario a medianoche
                if hh == 0 and mm == 0:
                    if self._ya_ejecuto_hoy:
                        self.log.emit("[DOSIS] Reset diario: listo para próxima ejecución.")
                    self._ya_ejecuto_hoy = False

                # ¿Ejecución programada?
                programada = (dow == self.weekday and hh == self.hour and mm == self.minute and not self._ya_ejecuto_hoy)

                # ¿Ejecución manual?
                manual = self._manual_trigger

                if programada or manual:
                    if manual:
                        self._manual_trigger = False
                        etiqueta = "manual"
                    else:
                        etiqueta = "programada"

                    self._ejecutar_dosificacion(etiqueta)

                    if programada:
                        self._ya_ejecuto_hoy = True

                time.sleep(1)  # chequeo cada 1s para reaccionar al manual
            except Exception as e:
                self.error.emit(f"[ERR] Loop dosificación: {e}")
                time.sleep(2)

        self.log.emit("[DOSIS] Hilo de dosificación finalizado.")

    # ---- Secuencia de dosificación ----
    def _ejecutar_dosificacion(self, etiqueta:str):
        stamp = datetime.now(self._tz).strftime('%Y-%m-%d %H:%M:%S')
        self.started_dose.emit(f"[{stamp}] Iniciando dosificación ({etiqueta})...")
        try:
            # Abrimos el puerto SOLO durante la secuencia
            with serial.Serial(self._port, self._baud, timeout=1) as arduino:
                time.sleep(2)  # por si Arduino hace reset al abrir

                # FloraMicro (Bomba 1)
                arduino.write(b'BON1\n')
                self.log.emit(" → Dosificando FloraMicro (B1 = 8.3 ml aprox)")
                time.sleep(self.t_bomba1 / 1000)
                arduino.write(b'BOFF1\n')
                time.sleep(0.4)

                # FloraGro (Bomba 2)
                arduino.write(b'BON2\n')
                self.log.emit(" → Dosificando FloraGro (B2 = 8.3 ml aprox)")
                time.sleep(self.t_bomba2 / 1000)
                arduino.write(b'BOFF2\n')
                time.sleep(0.4)

                # FloraBloom (Bomba 3)
                arduino.write(b'BON3\n')
                self.log.emit(" → Dosificando FloraBloom (B3 = 4.1 ml aprox)")
                time.sleep(self.t_bomba3 / 1000)
                arduino.write(b'BOFF3\n')

            stamp = datetime.now(self._tz).strftime('%Y-%m-%d %H:%M:%S')
            self.finished_dose.emit(f"[{stamp}] Dosificación completa ({etiqueta}).")
        except serial.SerialException as se:
            self.error.emit(f"[ERR] Serial: {se}")
        except Exception as e:
            self.error.emit(f"[ERR] Dosificación: {e}")

    # models/dosificador_thread.py (dentro de la clase DosificadorThread)
    def dosificar_bomba(self, pump:int, ms:int):
        if pump not in (1, 2, 3):
            self.error.emit(f"[ERR] Bomba inválida: {pump}")
            return
        if ms <= 0:
            self.error.emit(f"[ERR] Tiempo inválido para bomba {pump}: {ms} ms")
            return
        try:
            import serial, time
            with serial.Serial(self._port, self._baud, timeout=1) as arduino:
                time.sleep(2)  # por si resetea al abrir
                cmd_on  = f"BON{pump}\n".encode("utf-8")
                cmd_off = f"BOFF{pump}\n".encode("utf-8")
                arduino.write(cmd_on)
                self.log.emit(f" → Bomba {pump}: ON por {ms} ms")
                time.sleep(ms/1000.0)
                arduino.write(cmd_off)
            self.finished_dose.emit(f"[OK] Bomba {pump}: dosificación puntual completada ({ms} ms).")
        except Exception as e:
            self.error.emit(f"[ERR] Bomba {pump}: {e}")
