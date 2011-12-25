import os
import os.path
import simplejson
import settings

def filename(name):
    return os.path.join(settings.DATA_DIR, name + ".json")

def load(name):
    with file(filename(name)) as f:
        data = simplejson.loads(f.read())
    return data

def save(name, data):
    with file(filename(name), "w") as f:
        f.write(simplejson.dumps(data))

def exists(name):
    return os.path.exists(filename(name))

def delete(name):
    if exists(name):
        os.path.remove(filename(name))

def list():
    names = []
    for f in os.listdir(settings.DATA_DIR):
        if f.endswith(".json"):
            names.append(f[:-5])
    return names
