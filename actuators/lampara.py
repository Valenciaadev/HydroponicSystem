import serial
import time
from datetime import datetime

# Conectar con el Arduino
arduino = serial.Serial('/dev/ttyACM1', 9600, timeout=1)
time.sleep(2)  # Espera a que Arduino esté listo

estado_actual = None  # Guarda el último estado enviado: 'ON' o 'OFF'

# Configura el horario deseado
HORA_INICIO = 6
MINUTO_INICIO = 10
HORA_FIN = 22
MINUTO_FIN = 10

try:
    while True:
        now = datetime.now()
        hora = now.hour
        minuto = now.minute

        # Condición para encender
        debe_estar_encendida = (
            (hora > HORA_INICIO or (hora == HORA_INICIO and minuto >= MINUTO_INICIO)) and
            (hora < HORA_FIN or (hora == HORA_FIN and minuto < MINUTO_FIN))
        )

        if debe_estar_encendida and estado_actual != 'ON':
            arduino.write(b'ON\n')
            estado_actual = 'ON'
            print(f"[{now.strftime('%H:%M:%S')}] Lámpara ENCENDIDA")

        elif not debe_estar_encendida and estado_actual != 'OFF':
            arduino.write(b'OFF\n')
            estado_actual = 'OFF'
            print(f"[{now.strftime('%H:%M:%S')}] Lámpara APAGADA")

        time.sleep(10)  # Chequea cada 10 segundos

except KeyboardInterrupt:
    arduino.close()
    print("Conexión cerrada.")