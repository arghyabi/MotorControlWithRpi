from GpioManager import GpioManager
import time
import os
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
    print("System initialized. Checking Database...")

    rtDb = readRtDb()
    if rtDb == {}:
        print(f"No Database found; Create new Database...")
        writeRtDb(motorStatus="OFF", tankLevel=TANK_HEIGHT, configUpdateAvailable=True, mode="Auto")

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
    lastDistance    = 0
    lastDay         = datetime.now().day

    print("Reading initial distance...")
    while lastDistance <= 0:
        time.sleep(1)
        lastDistance = readDistance(gpio, ULTRASONIC_TRIG, ULTRASONIC_ECHO)
        print(f"Initial distance: {lastDistance} cm")

    try:
        lastCheckTime = time.time()
        lastRtDbCheck = time.time()
        preNightFillActive = False
        preNightFillStartTime = None

        # File modification tracking for efficient change detection
        lastRtDbModTime = 0
        rtDb = readRtDb()  # Initial read
        try:
            lastRtDbModTime = os.path.getmtime(RT_DB_FILE)
        except OSError:
            pass

        while True:
            currentTime = time.time()
            now = datetime.now()

            # Reset daily flags
            if now.day != lastDay:
                morning8RunDone = False
                evening9RunDone = False
                aftrn5RunDone   = False
                lastDay = now.day

            # Efficient database change detection using file modification time
            configUpdateAvailable = False
            needsDbRead = False

            # Check if file has been modified (lightweight operation)
            try:
                currentModTime = os.path.getmtime(RT_DB_FILE)
                if currentModTime != lastRtDbModTime:
                    print("Database Updated - Reading immediately")
                    needsDbRead = True
                    lastRtDbModTime = currentModTime
                elif currentTime - lastRtDbCheck >= DB_CHECK_INTERVAL:
                    # Periodic check even if file hasn't changed (for safety)
                    needsDbRead = True
            except OSError:
                # File doesn't exist or can't be accessed, try periodic read
                if currentTime - lastRtDbCheck >= DB_CHECK_INTERVAL:
                    needsDbRead = True

            if needsDbRead:
                rtDb = readRtDb()
                configUpdateAvailable = rtDb.get("configUpdateAvailable", False)
                lastRtDbCheck = currentTime
                if configUpdateAvailable:
                    print("Processing config update from web interface")
            # If no read needed, use cached rtDb (already initialized above)

            # Check for config updates for valves and mode
            if configUpdateAvailable:
                valve1Duration = rtDb.get("valve1Duration", VALVE1_DEFAULT_DURATION)
                valve2Duration = rtDb.get("valve2Duration", VALVE2_DEFAULT_DURATION)
                print(f"Updated valve durations: Valve1 = {valve1Duration} min, Valve2 = {valve2Duration} min")

            # Get current mode (default to Auto for backward compatibility)
            currentMode = rtDb.get("mode", "Auto")

            # Only check for scheduled valve operations once per minute to reduce processing
            # Valves operate regardless of mode (they have their own schedule)
            if now.second == 0:  # Only check at the beginning of each minute
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
                if now.hour == NOON_12PM and not aftrn5RunDone:
                    print("Afternoon run: Activating valves.")
                    gpio.output(VALVE1_PIN, True)
                    gpio.output(VALVE2_PIN, True)
                    valve1On = True
                    valve2On = True
                    valve1StartTime = currentTime
                    valve2StartTime = currentTime
                    aftrn5RunDone = True

                # Evening valve operation
                if now.hour == AFTERNOON_5PM and not evening9RunDone:
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
                while True:
                    distance = readDistance(gpio, ULTRASONIC_TRIG, ULTRASONIC_ECHO)
                    if distanceIsValid(distance, lastDistance):
                        print(f"Distance: {distance} cm")
                        lastDistance = distance
                        break
                    else:
                        print(f"Invalid distance reading: {distance} cm; SKIP;")
                        time.sleep(0.5)

                waterLevel = TANK_HEIGHT - distance
                motorStatus = rtDb.get("motorStatus", "OFF")
                print(f"!!!! Motor Status {motorStatus}; Config Update Available: {configUpdateAvailable} !!!!")


                if configUpdateAvailable:
                    # Apply config from rtDb.json both for Manual and Auto modes
                    if motorStatus == "ON":
                        gpio.output(MOTOR_PIN, True)
                        print(f">>> {currentMode} mode - Config update: Motor ON")
                    else:
                        gpio.output(MOTOR_PIN, False)
                        print(f">>> {currentMode} mode - Config update: Motor OFF")

                if currentMode == "Manual":
                    pass

                elif currentMode == "Auto":
                    # Standard automatic control logic
                    if isNightTime(): # Check if it's night time between 10 PM and 7 AM
                        print("Auto mode - Night time: Automatic motor control disabled. Only manual control available!")
                        preNightFillActive = False
                    else:
                        if now.hour == NIGHT_9PM and ifWaterLevelBelowTwoThird(waterLevel) and not preNightFillActive:
                            print(f"Auto mode - Pre-night: Water < 2/3, filling tank for {MAX_PRE_NIGHT_FILL_TIME} seconds...")
                            gpio.output(MOTOR_PIN, True)
                            motorStatus = "ON"
                            preNightFillActive = True
                            preNightFillStartTime = currentTime
                        elif preNightFillActive and (preNightFillStartTime is not None):
                            if ifWaterLevelAboveMax(waterLevel) or ((currentTime - preNightFillStartTime) > MAX_PRE_NIGHT_FILL_TIME):
                                gpio.output(MOTOR_PIN, False)
                                motorStatus = "OFF"
                                print("Auto mode - Tank filled before night.")
                                preNightFillActive = False
                            else:
                                gpio.output(MOTOR_PIN, True)
                                motorStatus = "ON"
                                print("Auto mode - Pre-night filling in progress...")
                        elif ifWaterLevelAboveMax(waterLevel): # Assuming sensor is at the top. Small distance means full.
                            gpio.output(MOTOR_PIN, False)
                            motorStatus = "OFF"
                            print("Auto mode - Tank full: Motor OFF")
                        elif ifWaterLevelBelowMin(waterLevel): # Large distance means empty
                            gpio.output(MOTOR_PIN, True)
                            motorStatus = "ON"
                            print("Auto mode - Tank empty: Motor ON")
                        else:
                            print(f"Auto mode - Tank level OK: No Motor Update; Currently Motor {motorStatus}")
                else:
                    print(f"Unknown mode '{currentMode}', defaulting to Auto mode behavior")
                    writeRtDb(mode = "Auto")

                lastCheckTime = currentTime

            # Update database if there are changes
            dbUpdates = {}
            if motorStatus != lastMotorStatus:
                dbUpdates["motorStatus"] = motorStatus
                lastMotorStatus = motorStatus

            if waterLevel != lastWaterLevel:
                dbUpdates["tankLevel"] = waterLevel
                lastWaterLevel = waterLevel

            if dbUpdates:
                print(f"Updating DB with: {dbUpdates}")
                writeRtDb(**dbUpdates)

            # Smart sleep: shorter sleep when config updates are expected
            if configUpdateAvailable:
                # If we just processed a config update, check again sooner
                time.sleep(0.5)  # Quick follow-up check
            else:
                # Normal operation - longer sleep for CPU efficiency
                time.sleep(1)
    except KeyboardInterrupt:
        cleanupGpio(gpio)


if __name__ == "__main__":
    main()
