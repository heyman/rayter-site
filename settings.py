import os
import os.path

REMOTE_DATA_BASE_URL = (
    "https://raw.githubusercontent.com/peterjaric/rayter-games/master/")
RAYTER_GITHUB_TOKEN = os.getenv("RAYTER_GITHUB_TOKEN")
RAYTER_USERS = os.getenv("RAYTER_USERS", "test:test")
RAYTER_GAMES_REPO=os.getenv("RAYTER_GAMES_REPO", "rayterbot/rayter-games")
RAYTER_METADATA_REPO=os.getenv("RAYTER_METADATA_REPO", "rayterbot/rayter-metadata")
