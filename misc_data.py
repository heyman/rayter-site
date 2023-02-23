import json

db_prefix = "misc_"
db_path = "data/misc_db.json"

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

def get_log():
    log = load("log")
    return log if log else []

def save_log(log):
    save("log", log)

def add_to_log(message):
    log = get_log()
    log.insert(0, message)
    save_log(log)
