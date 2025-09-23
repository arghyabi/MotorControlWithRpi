from GpioManager import GpioManager
import time
from datetime import datetime

from PinDescription import *
from Common         import *
from Utility        import *


def setupGpio(gpio:GpioManager):
    gpio.setup(MOTOR_PIN, True)
    gpio.setup(ULTRASONIC_TRIG, True)
    gpio.setup(ULTRASONIC_ECHO, False)
    gpio.setup(VALVE1_PIN, True)
    gpio.setup(VALVE2_PIN, True)

    gpio.output(MOTOR_PIN, False)
    gpio.output(VALVE1_PIN, False)
    gpio.output(VALVE2_PIN, False)


def cleanupGpio(gpio:GpioManager):
    gpio.output(MOTOR_PIN, False)
    gpio.output(VALVE1_PIN, False)
    gpio.output(VALVE2_PIN, False)
    gpio.cleanup()


def readDistance(gpio:GpioManager, trig, echo):
    # Ensure trigger is low
    gpio.output(trig, False)
    time.sleep(0.05)

    # Send a 10us pulse to trigger
    gpio.output(trig, True)
    time.sleep(0.00001)
    gpio.output(trig, False)

    # Wait for the echo pin to go high
    startTime = time.monotonic()
    while gpio.input(echo) == 0:
        if time.monotonic() - startTime > 1:
            return -1  # Timeout waiting for echo to start
    pulseStart = time.monotonic()

    # Wait for the echo pin to go low
    while gpio.input(echo) == 1:
        if time.monotonic() - pulseStart > 1:
            return -1  # Timeout waiting for echo to end
    pulseEnd = time.monotonic()

    pulseDuration = pulseEnd - pulseStart
    distance = pulseDuration * 17150
    distance = round(distance, 2)
    return distance


def isNightTime():
    now = datetime.now()
    hour = now.hour
    return hour >= NIGHT_10PM or hour < MORNING_7AM


def main():
    gpio = GpioManager()
    setupGpio(gpio)

    # Default valves and durations
    valve1Duration  = VALVE1_DEFAULT_DURATION
    valve2Duration  = VALVE2_DEFAULT_DURATION
    valve1On        = False
    valve2On        = False
    valve1StartTime = 0
    valve2StartTime = 0
    morning8RunDone = False
    aftrn5RunDone   = False
    evening9RunDone = False
    motorStatus     = "OFF"
    lastMotorStatus = "OFF"
    waterLevel      = 0
    lastWaterLevel  = 0
    lastDay         = datetime.now().day

    try:
        lastCheckTime = time.time()
        preNightFillActive = False
        preNightFillStart = None
        while True:
            currentTime = time.time()
            now = datetime.now()

            # Reset daily flags
            if now.day != lastDay:
                morning8RunDone = False
                evening9RunDone = False
                aftrn5RunDone   = False
                lastDay = now.day

            rtDb = readRtDb()
            configUpdateAvailable = rtDb.get("configUpdateAvailable", False)

            # Check for config updates for valves
            if configUpdateAvailable:
                valve1Duration = rtDb.get("valve1Duration", VALVE1_DEFAULT_DURATION)
                valve2Duration = rtDb.get("valve2Duration", VALVE2_DEFAULT_DURATION)
                print(f"Updated valve durations: Valve1={valve1Duration} min, Valve2={valve2Duration} min")

            # Morning valve operation
            if now.hour == MORNING_8AM and not morning8RunDone:
                print("Morning run: Activating valves.")
                gpio.output(VALVE1_PIN, True)
                gpio.output(VALVE2_PIN, True)
                valve1On = True
                valve2On = True
                valve1StartTime = currentTime
                valve2StartTime = currentTime
                morning8RunDone = True

            # Afternoon valve operation
            if now.hour == AFTERNOON_5PM and not aftrn5RunDone:
                print("Afternoon run: Activating valves.")
                gpio.output(VALVE1_PIN, True)
                gpio.output(VALVE2_PIN, True)
                valve1On = True
                valve2On = True
                valve1StartTime = currentTime
                valve2StartTime = currentTime
                aftrn5RunDone = True

            # Evening valve operation
            if now.hour == NIGHT_9PM and not evening9RunDone:
                print("Evening run: Activating valves.")
                gpio.output(VALVE1_PIN, True)
                gpio.output(VALVE2_PIN, True)
                valve1On = True
                valve2On = True
                valve1StartTime = currentTime
                valve2StartTime = currentTime
                evening9RunDone = True

            # Check to turn off valves
            if valve1On and (currentTime - valve1StartTime >= valve1Duration * 60):
                gpio.output(VALVE1_PIN, False)
                valve1On = False
                print("Valve 1 duration complete. Turned off.")

            if valve2On and (currentTime - valve2StartTime >= valve2Duration * 60):
                gpio.output(VALVE2_PIN, False)
                valve2On = False
                print("Valve 2 duration complete. Turned off.")

            # Original motor logic
            if currentTime - lastCheckTime >= CHECK_INTERVAL_SECONDS:
                distance = readDistance(gpio, ULTRASONIC_TRIG, ULTRASONIC_ECHO)
                print(f"Distance: {distance} cm")
                waterLevel = TANK_HEIGHT - distance
                rtDb = readRtDb()
                motorStatus = rtDb.get("motorStatus", "OFF")

                if configUpdateAvailable:
                    # Apply config from rtDb.json
                    if motorStatus == "ON":
                        gpio.output(MOTOR_PIN, True)
                        print("Config update: Motor ON")
                    else:
                        gpio.output(MOTOR_PIN, False)
                        print("Config update: Motor OFF")
                else:
                    # Automatic logic
                    motorStatus = "OFF"
                    if isNightTime(): # Check if it's night time between 10 PM and 7 AM
                        print("Night time: Automatic motor control disabled. Only manual control available!")
                        preNightFillActive = False
                    else:
                        if now.hour == NIGHT_9PM and waterLevel < ONE_THIRD_LEVEL and not preNightFillActive:
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
                        elif distance < TOP_EMPTY_DISTANCE: # Assuming sensor is at the top. Small distance means full.
                            gpio.output(MOTOR_PIN, False)
                            motorStatus = "OFF"
                            print("Tank full: Motor OFF")
                        elif distance > (TANK_HEIGHT - BOTTOM_FULL_DISTANCE): # Large distance means empty
                            gpio.output(MOTOR_PIN, True)
                            motorStatus = "ON"
                            print("Tank empty: Motor ON")
                        else:
                            gpio.output(MOTOR_PIN, False)
                            motorStatus = "OFF"
                            print("Tank level OK: Motor OFF")

                lastCheckTime = currentTime

            if configUpdateAvailable or motorStatus != lastMotorStatus or waterLevel != lastWaterLevel:
                writeRtDb(motorStatus = motorStatus, tankLevel = waterLevel, configUpdateAvailable = False)
                lastMotorStatus = motorStatus
                lastWaterLevel  = waterLevel

            time.sleep(0.1) # Sleep to reduce CPU usage
    except KeyboardInterrupt:
        cleanupGpio(gpio)


if __name__ == "__main__":
    main()
