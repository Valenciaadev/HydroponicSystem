# models/poolkit_thread.py
import serial
import time
from PyQt5.QtCore import QThread, pyqtSignal
from datetime import datetime
from models.database import guardar_mediciones_cada_6h

class PoolKitThread(QThread):
    datos_poolkit = pyqtSignal(dict)

    def __init__(self, port="/dev/ttyUSB0", baudrate=9600):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self._running = True
        self._ultima_hora_guardado = None

    def run(self):
        try:
            ser = serial.Serial(self.port, self.baudrate, timeout=1)
            print(f"✅ PoolKit conectado en {self.port}")
            time.sleep(2)

            while self._running:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    print("📥 [PoolKit] Línea recibida:", line)
                    try:
                        data = dict(item.split(":") for item in line.split(","))
                        temp = float(data.get("TEMP", 0.0))
                        ph = float(data.get("PH", 0.0))
                        orp = float(data.get("ORP", 0.0))

                        self.datos_poolkit.emit({
                            "temp_agua": temp,
                            "ph": ph,
                            "orp": orp,
                            "hora": datetime.now().strftime("%d/%m %H:%M:%S")
                        })

                        # 🕓 Guardar cada 6 horas
                        hora_actual = datetime.now().hour
                        minuto = datetime.now().minute
                        if minuto == 0 and hora_actual in [0, 6, 12, 18]:
                            if hora_actual != self._ultima_hora_guardado:
                                guardar_mediciones_cada_6h(ph, orp, temp)
                                self._ultima_hora_guardado = hora_actual

                    except Exception as e:
                        print(f"⚠️ [PoolKit] Línea inválida: {line} — Error: {e}")

                time.sleep(1)

        except Exception as e:
            print(f"❌ Error al iniciar PoolKitThread: {e}")

    def stop(self):
        self._running = False
        self.quit()
        self.wait()
