from PyQt5.QtCore import QThread, pyqtSignal
import RPi.GPIO as GPIO
import time
import serial
import re
from datetime import datetime

class NivelAguaThread(QThread):
    datos_nivel_agua = pyqtSignal(dict)

    def __init__(self, trig_pin=8, echo_pin=10, altura_total=45, serial_port='/dev/ttyACM0', baudrate=9600):
        super().__init__()
        self.trig = trig_pin
        self.echo = echo_pin
        self.altura_total = altura_total
        self.serial_port = serial_port
        self.baudrate = baudrate
        self._running = True

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.trig, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)

    def run(self):
        try:
            ser = serial.Serial(self.serial_port, self.baudrate, timeout=1)
            time.sleep(2)
            ser.reset_input_buffer()
            ser.write(b"LEER\r\n")  # ⬅️ Muy importante: \r\n
            ser.write(b"TON\r\n")   # ⬅️ Muy importante: \r\n

            while self._running:
                # 1. Medición de nivel de agua
                GPIO.output(self.trig, False)
                time.sleep(0.5)

                GPIO.output(self.trig, True)
                time.sleep(0.00001)
                GPIO.output(self.trig, False)

                pulse_start = time.time()
                timeout = pulse_start + 1

                while GPIO.input(self.echo) == 0 and time.time() < timeout:
                    pulse_start = time.time()
                while GPIO.input(self.echo) == 1 and time.time() < timeout:
                    pulse_end = time.time()

                pulse_duration = pulse_end - pulse_start
                distancia = pulse_duration * 17150
                nivel_agua = round(self.altura_total - distancia, 2) if 2 < distancia < 400 else None

                # 2. Leer temperatura y humedad del aire
                temp = None
                hum = None

                start_time = time.time()
                while time.time() - start_time < 2:  # Leer datos por 2 segundos
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if not line:
                        continue
                    print(f"📥 Línea serial: {line}")  # ⬅️ Depuración

                    if line.startswith("TEMP:"):
                        match = re.search(r'TEMP:([-+]?\d+(\.\d+)?)', line)
                        if match:
                            temp = float(match.group(1))

                    elif line.startswith("HUM:"):
                        match = re.search(r'HUM:(\d+(\.\d+)?)', line)
                        if match:
                            hum = float(match.group(1))

                # 3. Emitir si hay al menos un dato
                if nivel_agua is not None or temp is not None or hum is not None:
                    self.datos_nivel_agua.emit({
                        "nivel_agua": nivel_agua,
                        "temp_aire": temp,
                        "humedad_aire": hum,
                        "hora": datetime.now().strftime("%d/%m %H:%M:%S")
                    })

        except Exception as e:
            print(f"⚠️ Error en NivelAguaThread: {e}")

    def stop(self):
        self._running = False
        self.quit()
        self.wait()
        GPIO.cleanup()
