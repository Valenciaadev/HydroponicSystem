import serial
import time
import re

# Establecer conexión serial con Arduino
arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)  # Esperar que el Arduino reinicie

# Activar sensor de humedad
arduino.write(b"LEER\n")

ventilador_encendido = False
humedad = None

try:
    while True:
        line = arduino.readline().decode('utf-8', errors='ignore').strip()

        if not line:
            continue

        print("↪️ Arduino dice:", line)

        # Lectura de humedad
        if line.startswith("HUM:"):
            match = re.search(r'HUM:(\d+(\.\d+)?)', line)
            if match:
                humedad = float(match.group(1))
                print(f"💧 Humedad: {humedad}%")

                # Control del ventilador por humedad
                if humedad >= 70 and not ventilador_encendido:
                    print("⚙️ Humedad alta. Encendiendo ventilador.")
                    arduino.write(b"EN\n")
                    ventilador_encendido = True

                elif humedad <= 50 and ventilador_encendido:
                    print("🛑 Humedad normal. Apagando ventilador.")
                    arduino.write(b"AP\n")
                    ventilador_encendido = False

        time.sleep(0.5)

except KeyboardInterrupt:
    print("\n🛑 Saliendo... Apagando sensores y cerrando puerto.")
    arduino.write(b"PARAR\n")
    arduino.write(b"AP\n")  # Asegurar que el ventilador se apague
    arduino.close()