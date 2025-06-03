import serial
import time

arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)
arduino.write(b"LEER\r\n")  # prueba también b"LEER\n" o b"LEER"
time.sleep(0.5)

while True:
    line = arduino.readline().decode('utf-8', errors='ignore').strip()
    if line:
        print(f"Línea recibida: {line}")
