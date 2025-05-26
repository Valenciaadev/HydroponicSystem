# controllers/actuadores_serial.py
import serial
import time

# Conexión al Arduino del ventilador (/dev/ttyACM0)
try:
    arduino_ventilador = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    time.sleep(2)
    print("✅ Arduino ventilador conectado en /dev/ttyACM0")
except serial.SerialException as e:
    print("❌ Error al conectar con Arduino ventilador:", e)
    arduino_ventilador = None

# Conexión al Arduino de la lámpara (/dev/ttyACM1)
try:
    arduino_lampara = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    time.sleep(2)
    print("✅ Arduino lámpara conectado en /dev/ttyACM0")
except serial.SerialException as e:
    print("❌ Error al conectar con Arduino lámpara:", e)
    arduino_lampara = None

def enviar_comando(comando, dispositivo="ventilador"):
    """Envía un comando al Arduino según el tipo de dispositivo."""
    target = arduino_ventilador if dispositivo == "ventilador" else arduino_lampara
    if target and target.is_open:
        try:
            target.write(f"{comando}\n".encode())
            print(f"📤 Comando enviado a {dispositivo.upper()}: {comando}")
        except Exception as e:
            print(f"❌ Error al enviar comando a {dispositivo}: {e}")
