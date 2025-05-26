import serial
import time
from datetime import datetime
from models.database import guardar_mediciones_cada_6h

SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600

def run_serial_loop():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print("🔌 Conectado al puerto serial")
        time.sleep(2)

        ultima_hora = None

        while True:
            line = ser.readline().decode('utf-8').strip()
            if line:
                print("📥 Recibido:", line)
                try:
                    ph, orp, temp = map(float, line.split(','))

                    hora_actual = datetime.now().hour
                    if datetime.now().strftime('%M') == "00" and hora_actual != ultima_hora:
                        guardar_mediciones_cada_6h(ph, orp, temp)
                        ultima_hora = hora_actual

                except ValueError:
                    print("⚠️ Formato no válido:", line)

            time.sleep(1)

    except serial.SerialException as e:
        print("❌ Error de puerto serial:", e)
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("🔌 Puerto cerrado")
