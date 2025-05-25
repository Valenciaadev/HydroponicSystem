import serial
import time
import re

# Establecer conexión serial con Arduino (ajusta el puerto si es necesario)
arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)  # Espera a que el Arduino reinicie

# Enviar comando para empezar a leer temperatura
arduino.write(b"TON\n")

try:
    while True:
        line = arduino.readline().decode('utf-8', errors='ignore').strip()
        if line.startswith("TEMP:"):
            # Extraer solo el número usando expresión regular (puede ser negativo o decimal)
            match = re.search(r'TEMP:([-+]?\d+(\.\d+)?)', line)
            if match:
                temperatura = float(match.group(1))
                print(f"Temperatura: {temperatura} °C")
        elif line in ["high", "low"]:
            print(f"Advertencia: Temperatura {line}")

except KeyboardInterrupt:
    print("\nSaliendo...")
    arduino.write(b"TOFF\n")  # Detener lectura de temperatura
    arduino.close()