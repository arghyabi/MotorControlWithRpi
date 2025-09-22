import os

SCRIPT_PATH             = os.path.dirname(os.path.abspath(__file__))
BASE_PATH               = os.path.dirname(SCRIPT_PATH)

CONFIG_YAML_FILE        = os.path.join(BASE_PATH, "config.yaml")
RT_DB_FILE              = os.path.join(BASE_PATH, "rtDb.json")

INPUT                   = False
OUTPUT                  = True

PULL_UP                 = False
PULL_DOWN               = True

HIGH                    = True
LOW                     = False


WEBSITE_FOLDER          = "Web"
SCRIPT_FOLDER           = "Scripts"

CONFIG_UPDATE_AVAILABLE = True
NO_CONFIG_UPDATE        = False

TANK_HEIGHT             = 125  # Example tank height
TOP_EMPTY_DISTANCE      = 25
BOTTOM_FULL_DISTANCE    = 65
ONE_THIRD_LEVEL         = TANK_HEIGHT // 3

CHECK_INTERVAL_SECONDS  = 1
MAX_PRE_NIGHT_FILL_TIME = 600

MORNING_7AM             = 7
MORNING_8AM             = 8
EVENING_7PM             = 19
EVENING_8PM             = 20
NIGHT_10PM              = 22
NIGHT_9PM               = 21


VALVE1_DEFAULT_DURATION = 1  # in minutes
VALVE2_DEFAULT_DURATION = 1  # in minutes
