import os.path
import json
import settings

db_prefix = "rayter_"
db_path = "data/rayter_db.json"

def db_key(name):
    return db_prefix + name

def load(name):
    with open(db_path, "r") as f:
        db = json.load(f)
        if name in db:
            return db[name]
        else:
            return None

def save(name, data):
    with open(db_path, "r") as f:
        db = json.load(f)
    db[name] = data
    with open(db_path, "w") as f:
        json.dump(db, f)

def exists(name):
    with open(db_path, "r") as f:
        db = json.load(f)
        return name in db

def delete(name):
    with open(db_path, "r") as f:
        db = json.load(f)
    if name in db:
        del db[name]
        with open(db_path, "w") as f:
            json.dump(db, f)

def list():
    with open(db_path, "r") as f:
        db = json.load(f)
        names = []
        for key in db.keys():
            if key.startswith(db_prefix):
                names.append(key[len(db_prefix):])
        return names