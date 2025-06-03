# models/nivelagua_thread.py
from PyQt5.QtCore import QThread, pyqtSignal
import RPi.GPIO as GPIO
import time
from datetime import datetime

class NivelAguaThread(QThread):
    datos_nivel_agua = pyqtSignal(dict)

    def __init__(self, trig_pin=8, echo_pin=10, altura_total=45):
        super().__init__()
        self.trig = trig_pin
        self.echo = echo_pin
        self.altura_total = altura_total
        self._running = True

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.trig, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)

    def run(self):
        while self._running:
            try:
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

                if 2 < distancia < 400:
                    nivel_agua = round(self.altura_total - distancia, 2)
                    self.datos_nivel_agua.emit({
                        "nivel_agua": nivel_agua,
                        "hora": datetime.now().strftime("%d/%m %H:%M:%S")
                    })
                else:
                    print("❌ Lectura fuera de rango.")

                time.sleep(2)

            except Exception as e:
                print(f"⚠️ Error en NivelAguaThread: {e}")

    def stop(self):
        self._running = False
        self.quit()
        self.wait()
        GPIO.cleanup()
