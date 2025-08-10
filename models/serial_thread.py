# models/serial_thread.py
import serial
import time
from PyQt5.QtCore import *
from datetime import datetime
from threading import Thread
from models.database import guardar_mediciones_cada_6h

SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600

class SerialReaderThread(QThread):
    datos_actualizados = pyqtSignal(dict)  # 👈 señal que enviará los datos

    def __init__(self):
        super().__init__()
        self._running = True
        self._ultima_hora_guardado = None

    def run(self):
        import serial
        from models.database import guardar_mediciones_cada_6h
        from datetime import datetime
        import time

        while self._running:
            try:
                ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
                # print(f"✅ Conectado a {SERIAL_PORT}")
                time.sleep(2)

                while self._running and ser.is_open:
                    try:
                        line = ser.readline().decode('utf-8').strip()
                        if line:
                            try:
                                data = dict(item.split(':') for item in line.split(','))
                                temp = float(data['TEMP'])
                                ph = float(data['PH'])
                                orp = float(data['ORP'])

                                self.datos_actualizados.emit({
                                    "temp_agua": temp,
                                    "ph": ph,
                                    "orp": orp,
                                    "hora": datetime.now().strftime("%d/%m %H:%M:%S")
                                })

                                hora_actual = datetime.now().hour
                                minuto = datetime.now().minute
                                if minuto == 00 and hora_actual in [0, 6, 12, 18]:
                                    if hora_actual != self._ultima_hora_guardado:
                                        guardar_mediciones_cada_6h(ph, orp, temp)
                                        self._ultima_hora_guardado = hora_actual
                            except Exception as e:
                                print(f"⚠️ Línea inválida: {line} — Error: {e}")

                        time.sleep(1)

                    except serial.SerialException as e:
                        print(f"🔌 Error de lectura: {e}")
                        break

            except serial.SerialException as e:
                print(f"❌ No se pudo conectar a {SERIAL_PORT}: {e}")
            
            # Esperamos antes de intentar reconectar
            time.sleep(5)


    def stop(self):
        self._running = False
        self.quit()
        self.wait()