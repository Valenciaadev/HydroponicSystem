import serial
import time

# Cambia esto al puerto correcto de tu dispositivo
SERIAL_PORT = '/dev/ttyUSB0'   
BAUD_RATE = 9600

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print("Conectado al puerto serial:", SERIAL_PORT)
    time.sleep(2)  # Esperar a que el microcontrolador arranque

    while True:
        line = ser.readline().decode('utf-8').strip()
        if line:
            print("Datos recibidos:", line)

except serial.SerialException as e:
    print("Error al conectar con el puerto serial:", e)

except KeyboardInterrupt:
    print("\nLectura interrumpida por el usuario.")

finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Puerto serial cerrado.")