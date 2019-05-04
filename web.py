from auth import Auth
from flask import Flask, Response, abort, request

import logging
import web_impl
import settings

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("github").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("watchdog").setLevel(logging.WARNING)

app = Flask(__name__)
auth = Auth(app, settings.RAYTER_USERS)


@app.route("/")
def index():
    return web_impl.index()


@app.route("/refresh/<name>")
def refresh(name):
    return web_impl.refresh(name)


@app.route("/refresh_game/<name>")
def refresh_game(name):
    return web_impl.refresh_game(name)


@app.route("/refresh_all")
def refresh_all():
    return web_impl.refresh_all()


@app.route("/post_push", methods=["POST"])
def post_push():
    return web_impl.post_push()


@app.route("/favicon.ico")
def favicon():
    abort(404)


@app.route("/<game_name>")
def show_game(game_name):
    return web_impl.show_game(game_name)

@app.route("/<game_name>.json")
def show_game_json(game_name):
    return web_impl.show_game_json(game_name)


@app.route("/new", methods=["POST", "GET"])
@auth.required
def new_result():
    if request.method == "POST":
        return web_impl.post_new_result()
    else:
        return web_impl.get_new_result()


# FIXME: use posted data from Github instead of going there and fetching it
# with default implementation of refresh_users
@app.route("/post_push_users", methods=["POST"])
def post_push_users():
    return refresh_users()


@app.route("/refresh_users")
def refresh_users():
    return web_impl.refresh_users()


@app.route("/user/<name>")
def show_user(name):
    return web_impl.show_user(name)

@app.route("/achievements")
def achievements():
    return web_impl.show_achievements()

if __name__ == "__main__":
    app.run(debug=True)
