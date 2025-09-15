import json
import os
from Common import RT_DB_FILE

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
