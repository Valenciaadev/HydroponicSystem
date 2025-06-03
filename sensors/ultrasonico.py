import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

TRIG = 8
ECHO = 10
ALTURA_TOTAL = 45  # cm, altura desde sensor al fondo del recipiente

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def medir_distancia():
    GPIO.output(TRIG, False)
    time.sleep(0.5)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    pulse_start = time.time()
    timeout = pulse_start + 1

    while GPIO.input(ECHO) == 0 and time.time() < timeout:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1 and time.time() < timeout:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distancia = pulse_duration * 17150
    return round(distancia, 2)

try:
    while True:
        distancia = medir_distancia()

        if distancia < 2 or distancia > 400:
            print("❌ Lectura fuera de rango.")
            continue

        nivel_agua = ALTURA_TOTAL - distancia
        nivel_agua = round(nivel_agua, 2)

        print(f"💧 Nivel de agua: {nivel_agua} cm")

        if 11.5 <= nivel_agua <= 13.5:
            print("✅ Nivel óptimo")
        elif nivel_agua < 11.5:
            print("⚠️ Nivel BAJO")
        elif nivel_agua > 13.5:
            print("⚠️ Nivel ALTO")

        time.sleep(2)

except KeyboardInterrupt:
    GPIO.cleanup()
