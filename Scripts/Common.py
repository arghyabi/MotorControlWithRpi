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

# ------[_]--------      <------------|
# |               |         25        |
# |...............|      <------      |
# |               |            |      |
# |               |            |      |
# |               |            |      |
# |               |            |     125
# |               |            |      |
# |               |           70      |
# |               |            |      |
# |               |            |      |
# |               |            |      |
# |...............|      <------      |
# |               |          |        |
# |               |         30        |
# |               |          |        |
# -----------------      <------------|

TANK_HEIGHT             = 125  # Example tank height
TOP_EMPTY_DISTANCE      = 25
BOTTOM_FULL_DISTANCE    = 30

MAX_WATER_LEVEL         = TANK_HEIGHT - TOP_EMPTY_DISTANCE
TWO_THIRD_LEVEL         = MAX_WATER_LEVEL // 3 * 2  # Two-thirds full level

CHECK_INTERVAL_SECONDS  = 1
MAX_PRE_NIGHT_FILL_TIME = 600

NIGHT_12AM              = 0
NIGHT_1AM               = 1
NIGHT_2AM               = 2
NIGHT_3AM               = 3
NIGHT_4AM               = 4
NIGHT_5AM               = 5
MORNING_6AM             = 6
MORNING_7AM             = 7
MORNING_8AM             = 8
MORNING_9AM             = 9
MORNING_10AM            = 10
MORNING_11AM            = 11
NOON_12PM               = 12
AFTERNOON_1PM           = 13
AFTERNOON_2PM           = 14
AFTERNOON_3PM           = 15
AFTERNOON_4PM           = 16
AFTERNOON_5PM           = 17
EVENING_6PM             = 18
EVENING_7PM             = 19
EVENING_8PM             = 20
NIGHT_9PM               = 21
NIGHT_10PM              = 22
NIGHT_11PM              = 23


VALVE1_DEFAULT_DURATION = 1  # in minutes
VALVE2_DEFAULT_DURATION = 1  # in minutes
