import os.path

DIR = os.path.dirname(os.path.realpath(__file__))
DIR = "/".join(DIR.split("/")[:-2])

SITE_CACHE = os.path.join(DIR + "/data/NTGSPI_cache.json")
LOCAL_DATABASE = os.path.join(DIR + "/data/localDB.db")
TELEGRAM_CRED = os.path.join(DIR + "/data/credentials.json")
MAP_FILE = os.path.join(DIR + "/data/map.csv")
MAP_LEGEND = os.path.join(DIR + "/data/map_titles.json")