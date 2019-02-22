import os
import os.path
import json
import settings
import redis

redis = redis.from_url(settings.REDIS_URL)

def rayter_name(name):
    return "rayter_" + name

def load(name):
    raw = redis.get(rayter_name(name))
    return json.loads(raw)

def save(name, data):
    redis.set(rayter_name(name), json.dumps(data))

def exists(name):
    return redis.exists(rayter_name(name))

def delete(name):
    if exists(name):
        redis.delete(rayter_name(name))

def list():
    names = []
    for key in redis.keys():
        if key.startswith("rayter_"):
            names.append(key[7:])
    return names
