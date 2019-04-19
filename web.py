import os.path
from StringIO import StringIO

from flask import Flask, render_template, request, redirect, Response
from time import strftime
import json
import requests

import logging
logging.basicConfig(level=logging.DEBUG)

from rayter.main import parse_file
from rayter.game_parser import GamesParser
from rayter.rater import Rater

import github_api
import settings
import data


app = Flask(__name__)


def get_game_file(name):
    """
    Fetch file from github. If github responds with 404, return None, else return content as a string.
    """
    url = settings.REMOTE_DATA_BASE_URL + name + ".txt"

    response = requests.get(url)

    if response.status_code == 200:
        return response.text
    elif response.status_code == 404:
        return None
    else:
        raise requests.HTTPError("Unknown HTTP error when fetching " + name)


def refresh_from_game_file(name):
    """
    Fetch file from github and re-calculate ratings. If github responds with 404,
    the data will be deleted.
    """
    try:
        content = get_game_file(name)

        if content == None:
            print "Not found"
            data.delete(name)
            return False
        else:
            parser = GamesParser(StringIO(content), name)
            games = parser.parse_file()
            rater = Rater(games)
            ratings = rater.rate_games(parser.score_type)
            game = {
                "game_name": parser.game_name,
                "ratings": ratings,
                "count": len(games),
            }
            data.save(name, game)
            return True
    except requests.HTTPError as e:
        logging.error(e)


@app.route("/")
def index():
    game_names = sorted(data.list())
    games = []
    global_ratings = {}

    for name in game_names:
        game = data.load(name)
        players = game['ratings']
        print game
        games.append((name, game['game_name'], players, game['count']))

        for player_name, game_count, rating, delta in players:
            if player_name not in global_ratings:
                global_ratings[player_name] = []
            global_ratings[player_name].append(rating)

    average_ratings = []
    for player_name, player_ratings in global_ratings.items():
        if len(player_ratings) > 3:
            average_ratings.append(
                (player_name,
                 float(sum(player_ratings)) / len(player_ratings)))

    print average_ratings

    average_ratings.sort(key=lambda p: p[1], reverse=True)

    return render_template("index.html", games=games, top_list=average_ratings)


@app.route("/refresh/<name>")
def refresh(name):
    refresh_from_game_file(name)
    return "done"


@app.route("/refresh_game/<name>")
def refresh_game(name):
    if refresh_from_game_file(name):
        return redirect("/" + name)
    else:
        return "Could not find game"


@app.route("/refresh_all")
def refresh_all():
    game_names = data.list()
    for name in game_names:
        refresh_from_game_file(name)
    return "done"


@app.route("/post_push", methods=["POST"])
def post_push():
    print "post_push"
    updated = {}
    data = request.form["payload"]
    print "data:", data
    push_info = json.loads(data)
    for commit in push_info["commits"]:
        for name in commit.get("added", []) + commit.get(
                "removed", []) + commit.get("modified", []):
            updated[name] = True

    for name in updated.iterkeys():
        if name.endswith(".txt"):
            refresh_from_game_file(name[:-4])

    return "done"


@app.route("/favicon.ico")
def favicon():
    return Response("Not found", status=404)


@app.route("/<name>")
def show_game(name):
    game_data = data.load(name)
    print "game_data:", game_data
    return render_template("game.html",
                           name=name,
                           players=game_data['ratings'],
                           game_name=game_data['game_name'])


@app.route("/new", methods=["POST", "GET"])
def new_result():
    if request.method == 'POST':
        return post_new_result()
    else:
        return get_new_result()


def get_new_result():
    games = sorted(data.list())
    players_set = set()

    for name in games:
        game = data.load(name)
        players = game['ratings']
        for player in players:
            name = player[0]
            players_set.add(name)

    players_list = list(players_set)
    players_list.sort()

    return render_template("new.html", players=players_list, games=games)


def post_new_result():
    index = 0
    match = {
        "results": [],
        "time": strftime("%Y-%m-%d %H:%M"),
        "game": request.form.get("game")
    }

    for player in request.form.getlist('player'):
        score = request.form.getlist('score')[index]
        if player and score:
            match["results"].append((player, score))
        index += 1

    update_on_github(match)

    return render_template("new_display.html", match=match)


def update_on_github(match):
    name = match['game']
    try:
        content = get_game_file(name)

        if content == None:
            print "Not found"
            return False
        else:
            new_content = content + "\n"
            new_content += "game " + match['time'] + "\n"
            for (player, score) in match['results']:
                new_content += player + " " + score + "\n"
            github_api.update('rayter-games', name + '.txt', new_content,
                              'New game added at ' + strftime('%H:%M:%S'))
            return True
    except requests.HTTPError as e:
        logging.error(e)


if __name__ == '__main__':
    app.run(debug=True)
