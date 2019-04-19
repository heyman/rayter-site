import os
import os.path

REMOTE_DATA_BASE_URL = (
    "https://raw.githubusercontent.com/rayterbot/rayter-games/master/")
REDIS_URL = os.getenv("REDISTOGO_URL", "redis://localhost:6379")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
