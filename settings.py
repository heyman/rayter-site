import os
import os.path

ROOT_DIR = os.path.dirname(__file__)
REMOTE_DATA_BASE_URL = "https://raw.github.com/peterjaric/rayter-games/master/"
DATA_DIR = os.environ.get("EPIO_DATA_DIRECTORY", os.path.join(ROOT_DIR, "data"))
