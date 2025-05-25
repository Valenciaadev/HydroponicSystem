# models/serial_thread.py
import serial
import time
from datetime import datetime
from threading import Thread
from models.database import guardar_mediciones_cada_6h

SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600

class SerialReaderThread(Thread):
    def __init__(self):
        super().__init__()
        self._running = True
        self._ultima_hora_guardado = None

    def run(self):
        try:
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            print("✅ Conectado al puerto serial")
            time.sleep(2)

            while self._running:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    print("📥 Línea recibida:", line)
                    try:
                        # Parseo con etiquetas
                        data = dict(item.split(':') for item in line.split(','))
                        temp = float(data['TEMP'])
                        ph = float(data['PH'])
                        orp = float(data['ORP'])

                        # Solo guardar a las horas exactas y una vez por hora
                        hora_actual = datetime.now().hour
                        minuto = datetime.now().minute
                        if minuto == 0 and hora_actual in [0, 6, 12, 18]:
                            if hora_actual != self._ultima_hora_guardado:
                                guardar_mediciones_cada_6h(ph, orp, temp)
                                self._ultima_hora_guardado = hora_actual

                    except (ValueError, KeyError) as e:
                        print("⚠️ Formato inválido o incompleto:", line)

                time.sleep(1)

        except serial.SerialException as e:
            print("❌ Error de conexión serial:", e)

        finally:
            if 'ser' in locals() and ser.is_open:
                ser.close()
                print("🔌 Puerto serial cerrado")

    def stop(self):
        self._running = False
