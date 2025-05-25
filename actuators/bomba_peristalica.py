import serial
import time
from datetime import datetime

# === CONFIGURACIÓN SERIAL ===
arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)  # Esperar que Arduino se reinicie

# === CONFIGURACIÓN HORARIO DE DOSIFICACIÓN ===
HORA_EJECUCION = 7  # 7:00 AM
MINUTO_EJECUCION = 0
ya_ejecuto_hoy = False

# === TIEMPOS DE DOSIFICACIÓN (en milisegundos) ===
TIEMPO_BOMBA1 = 3452  # FloraMicro (8.3 ml)
TIEMPO_BOMBA2 = 3452  # FloraGro (8.3 ml)
TIEMPO_BOMBA3 = 1708  # FloraBloom (4.1 ml)

# === MANTENER BOMBA DE AGUA ENCENDIDA ===
arduino.write(b'BAON\n')
print("[INFO] Bomba de agua encendida permanentemente.")

try:
    while True:
        now = datetime.now()
        hora = now.hour
        minuto = now.minute

        if hora == HORA_EJECUCION and minuto == MINUTO_EJECUCION and not ya_ejecuto_hoy:
            print(f"[{now.strftime('%H:%M:%S')}] Iniciando dosificación...")

            # FloraMicro
            arduino.write(b'BON1\n')
            print(" → Dosificando FloraMicro (8.3 ml)")
            time.sleep(TIEMPO_BOMBA1 / 1000)
            arduino.write(b'BOFF1\n')

            time.sleep(0.5)

            # FloraGro
            arduino.write(b'BON2\n')
            print(" → Dosificando FloraGro (8.3 ml)")
            time.sleep(TIEMPO_BOMBA2 / 1000)
            arduino.write(b'BOFF2\n')

            time.sleep(0.5)

            # FloraBloom
            arduino.write(b'BON3\n')
            print(" → Dosificando FloraBloom (4.1 ml)")
            time.sleep(TIEMPO_BOMBA3 / 1000)
            arduino.write(b'BOFF3\n')

            print(f"[{now.strftime('%H:%M:%S')}] Dosificación completa.")
            ya_ejecuto_hoy = True  # Solo una vez al día

        # Reset diario a la medianoche
        if hora == 0 and minuto == 0:
            ya_ejecuto_hoy = False

        time.sleep(10)

except KeyboardInterrupt:
    print("\n[INFO] Programa detenido por el usuario.")
    arduino.write(b'BAOFF\n')  # Apagar bomba de agua (opcional)
    arduino.close()