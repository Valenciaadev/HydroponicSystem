# models/serial_ambiente_thread.py
import serial
import time
import re
from PyQt5.QtCore import QThread, pyqtSignal
from datetime import datetime

class AmbienteThread(QThread):
    datos_actualizados = pyqtSignal(dict)

    def __init__(self, port="/dev/ttyACM0", baudrate=9600):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self._running = True

    def run(self):
        try:
            arduino = serial.Serial(self.port, self.baudrate, timeout=1)
            print(f"🌡️ Arduino ambiente conectado en {self.port}")
            time.sleep(2)

            # Enviar comandos para iniciar ambas lecturas
            arduino.write(b"TON\n")
            time.sleep(0.2)
            arduino.write(b"LEER\n")

            while self._running:
                line = arduino.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    print("📥 [Ambiente] Línea recibida:", line)

                    temp_match = re.search(r'TEMP:([-+]?\d+(\.\d+)?)', line)
                    hum_match = re.search(r'HUM:(\d+(\.\d+)?)', line)

                    data = {"hora": datetime.now().strftime("%d/%m %H:%M:%S")}
                    if temp_match:
                        data["temp_ambiente"] = float(temp_match.group(1))
                    if hum_match:
                        data["humedad"] = float(hum_match.group(1))

                    if "temp_ambiente" in data or "humedad" in data:
                        self.datos_actualizados.emit(data)

                time.sleep(1)

        except Exception as e:
            print(f"❌ Error en AmbienteThread: {e}")

    def stop(self):
        self._running = False
        self.quit()
        self.wait()

