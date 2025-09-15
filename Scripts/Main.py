from GpioManager import GpioManager
import time
from datetime import datetime

from PinDescription import *
from Common         import *
from Utility        import *


def setupGpio(gpio:GpioManager):
    gpio.setup(MOTOR_PIN, True)
    gpio.setup(ULTRASONIC_EMPTY_TRIG, True)
    gpio.setup(ULTRASONIC_EMPTY_ECHO, False)
    gpio.setup(ULTRASONIC_FULL_TRIG, True)
    gpio.setup(ULTRASONIC_FULL_ECHO, False)
    gpio.output(MOTOR_PIN, False)


def cleanupGpio(gpio:GpioManager):
    gpio.output(MOTOR_PIN, False)
    gpio.cleanup()


def readDistance(gpio:GpioManager, trig, echo):
    gpio.output(trig, False)
    time.sleep(0.05)
    gpio.output(trig, True)
    time.sleep(0.00001)
    gpio.output(trig, False)

    pulseStart = None
    pulseEnd = None
    timeout = time.time() + 1
    while gpio.input(echo) == 0:
        pulseStart = time.time()
        if time.time() > timeout:
            return -1
    while gpio.input(echo) == 1:
        pulseEnd = time.time()
        if time.time() > timeout:
            return -1
    if pulseStart is None or pulseEnd is None:
        return -1
    pulseDuration = pulseEnd - pulseStart
    distance = pulseDuration * 17150
    distance = round(distance, 2)
    return distance


def isNightTime():
    now = datetime.now()
    hour = now.hour
    return hour >= 22 or hour < 7


def main():
    gpio = GpioManager()
    setupGpio(gpio)
    try:
        lastCheckTime = time.time()
        preNightFillActive = False
        preNightFillStart = None
        while True:
            currentTime = time.time()
            if currentTime - lastCheckTime >= CHECK_INTERVAL_SECONDS:
                emptyDistance = readDistance(gpio, ULTRASONIC_EMPTY_TRIG, ULTRASONIC_EMPTY_ECHO)
                fullDistance = readDistance(gpio, ULTRASONIC_FULL_TRIG, ULTRASONIC_FULL_ECHO)
                print(f"Empty Distance: {emptyDistance} cm, Full Distance: {fullDistance} cm")
                waterLevel = TANK_HEIGHT - emptyDistance
                now = datetime.now()
                rtDb = readRtDb()
                configUpdateAvailable = rtDb.get("configUpdateAvailable", False)
                motorStatus = rtDb.get("motorStatus", "OFF")

                if configUpdateAvailable:
                    # Apply config from rtDb.json
                    if motorStatus == "ON":
                        gpio.output(MOTOR_PIN, True)
                        print("Config update: Motor ON")
                    else:
                        gpio.output(MOTOR_PIN, False)
                        print("Config update: Motor OFF")
                    # Reset configUpdateAvailable after applying
                    writeRtDb(motorStatus=motorStatus, tankLevel=waterLevel, configUpdateAvailable=False)
                else:
                    # Automatic logic
                    motorStatus = "OFF"
                    if isNightTime():
                        gpio.output(MOTOR_PIN, False)
                        motorStatus = "OFF"
                        print("Night time: Motor OFF")
                        preNightFillActive = False
                    else:
                        if now.hour == 21 and waterLevel < ONE_THIRD_LEVEL and not preNightFillActive:
                            print("Pre-night: Water < 1/3, filling tank...")
                            gpio.output(MOTOR_PIN, True)
                            motorStatus = "ON"
                            preNightFillActive = True
                            preNightFillStart = currentTime
                        elif preNightFillActive:
                            if waterLevel >= TANK_HEIGHT or (preNightFillStart is not None and currentTime - preNightFillStart > MAX_PRE_NIGHT_FILL_TIME):
                                gpio.output(MOTOR_PIN, False)
                                motorStatus = "OFF"
                                print("Tank filled before night.")
                                preNightFillActive = False
                            else:
                                gpio.output(MOTOR_PIN, True)
                                motorStatus = "ON"
                                print("Pre-night filling in progress...")
                        elif fullDistance < 5:
                            gpio.output(MOTOR_PIN, False)
                            motorStatus = "OFF"
                            print("Tank full: Motor OFF")
                        elif emptyDistance > (TANK_HEIGHT - 5):
                            gpio.output(MOTOR_PIN, True)
                            motorStatus = "ON"
                            print("Tank empty: Motor ON")
                        else:
                            gpio.output(MOTOR_PIN, False)
                            motorStatus = "OFF"
                            print("Tank level OK: Motor OFF")
                    writeRtDb(motorStatus=motorStatus, tankLevel=waterLevel, configUpdateAvailable=False)
                lastCheckTime = currentTime
            time.sleep(0.1)
            # Short sleep to reduce CPU usage and maintain responsiveness
    except KeyboardInterrupt:
        cleanupGpio(gpio)


if __name__ == "__main__":
    main()
