import json
import os
from Common import *

def readRtDb():
    try:
        with open(RT_DB_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {}


def writeRtDb(motorStatus=None, tankLevel=None, configUpdateAvailable=None):
    db = readRtDb()
    if motorStatus is not None:
        db["motorStatus"] = motorStatus
    if tankLevel is not None:
        db["tankLevel"] = tankLevel
    if configUpdateAvailable is not None:
        db["configUpdateAvailable"] = configUpdateAvailable
    try:
        with open(RT_DB_FILE, 'w') as f:
            json.dump(db, f)
    except Exception as e:
        print(f"Error writing to {RT_DB_FILE}: {e}")


def ifWaterLevelBelowTwoThird(waterLevel):
    # Allow a margin of +/- 5 cm around TWO_THIRD_LEVEL for consistency (hysteresis)
    margin = 5
    if waterLevel < (TWO_THIRD_LEVEL - margin):
        return True
    elif waterLevel > (TWO_THIRD_LEVEL + margin):
        return False
    else:
        return False


def ifWaterLevelAboveMax(waterLevel):
    # Allow a margin of +/- 5 cm around MAX_WATER_LEVEL for consistency (hysteresis)
    margin = 5
    if waterLevel > (MAX_WATER_LEVEL + margin):
        return True
    elif waterLevel < (MAX_WATER_LEVEL - margin):
        return False
    else:
        return False


def ifWaterLevelBelowMin(waterLevel):
    # Allow a margin of +/- 5 cm around BOTTOM_FULL_DISTANCE for consistency (hysteresis)
    margin = 5
    minLevel = TANK_HEIGHT - BOTTOM_FULL_DISTANCE
    if waterLevel < (minLevel - margin):
        return True
    elif waterLevel > (minLevel + margin):
        return False
    else:
        return False
