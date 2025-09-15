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

TANK_HEIGHT             = 60  # Example tank height
ONE_THIRD_LEVEL         = TANK_HEIGHT / 3

CHECK_INTERVAL_SECONDS  = 1
MAX_PRE_NIGHT_FILL_TIME = 600
