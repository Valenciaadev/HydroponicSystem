import serial
import time
import re

# Establecer conexión serial con Arduino
arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)  # Espera que el Arduino reinicie

# Enviar comando para empezar a leer
arduino.write(b"LEER\n")

try:
    while True:
        line = arduino.readline().decode('utf-8', errors='ignore').strip()
        if line.startswith("HUM:"):
            # Extraer solo el número usando expresión regular
            match = re.search(r'HUM:(\d+(\.\d+)?)', line)
            if match:
                humedad = float(match.group(1))
                print(f"Humedad: {humedad}")

except KeyboardInterrupt:
    print("\nSaliendo...")
    # Enviar comando para detener lectura
    arduino.write(b"PARAR\n")
    arduino.close()
