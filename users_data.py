import os
import os.path
import json
import settings
import redis

redis = redis.from_url(settings.REDIS_URL)
redis_prefix = "users_"


def redis_key(user_name):
    return redis_prefix + user_name


def load(user_name):
    raw = redis.get(redis_key(user_name))
    if raw:
        return json.loads(raw)
    else:
        return None

def save(user_name, data):
    redis.set(redis_key(user_name), json.dumps(data))


def save_users(users):
    for user in users:
        save(user['userName'], user)


def exists(user_name):
    return redis.exists(redis_key(user_name))


def delete(user_name):
    if exists(user_name):
        redis.delete(redis_key(user_name))


def list_names():
    names = []
    for key in redis.keys():
        if key.startswith(redis_prefix):
            names.append(key[len(redis_prefix):])
    return names

def list_users():
    users = {}
    for key in redis.keys():
        if key.startswith(redis_prefix):
            name = key[len(redis_prefix):]
            users[name] = load(name)
    return users
