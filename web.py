import os.path
from StringIO import StringIO

from flask import Flask, render_template, request, redirect, Response, abort

from time import strftime
import json
import requests
import numpy

import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("github").setLevel(logging.WARNING)
logging.getLogger("watchdog").setLevel(logging.WARNING)

from rayter.main import parse_file
from rayter.game_parser import GamesParser
from rayter.rater import Rater

from pprint import pprint

import game_content
import settings
import data
from auth import Auth

import game_content

app = Flask(__name__)
auth = Auth(app, settings.RAYTER_USERS)


def get_game_file(name):
    """
    Fetch game file.
    """
    return game_content.get(name + ".txt")


def refresh_from_game_file(name):
    """
    Fetch game file and re-calculate ratings. If the game file does not exist, the data will be deleted.
    """
    try:
        content = get_game_file(name)

        if content == None:
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


def top_list_ratings(ratings):
    average_ratings = []
    for player_name, player_data in ratings.items():
        # player_data is a list of tuples of two numbers containing these values:
        # ("player's rating in a game", "number of matches the player has played in that game")

        if len(player_data) > 3:
            # Create a list of ratings for all games
            player_ratings = map(lambda tuple: tuple[0], player_data)
            # Create a matching list of the number of played matches for each game
            player_counts = map(lambda tuple: tuple[1], player_data)

            # Add a "virtual" match where everyone has a rating of 1000 to make high ratings for players with few games count less
            player_ratings.append(1000)
            # Increasing the virtual player count to more than 10 would make changes even slower, and vice versa.
            # Let's try 10 for now.
            player_counts.append(10)

            average = numpy.average(player_ratings, weights=player_counts)
            average_ratings.append((player_name, average))

    average_ratings.sort(key=lambda p: p[1], reverse=True)

    return average_ratings


def top_list_placements(placements):
    average_placements = []
    for player_name, player_data in placements.items():
        # player_data is a list of tuples of two numbers containing these values:
        # ("player's placement in a game as a number between 0 and 1, 0 is better", "number of matches the player has played in that game")

        # If player has played at least 3 games
        if len(player_data) >= 3:
            # Create a list of placements for all games
            player_placements = map(lambda tuple: tuple[0], player_data)
            # Create a matching list of the number of played matches for each game
            player_counts = map(lambda tuple: tuple[1], player_data)

            average = numpy.average(player_placements, weights=player_counts)
            average_placements.append((player_name, average))

    average_placements.sort(key=lambda (player_name, average): average)

    # Don't show players with a placement below 50% on the top list
    average_placements = filter(lambda (player_name, average): average <= 0.5,
                                average_placements)

    return average_placements


@app.route("/")
def index():
    game_names = sorted(data.list())
    games = []
    global_ratings = {}
    global_placements = {}

    for name in game_names:
        game = data.load(name)
        players = game["ratings"]
        games.append((name, game["game_name"], players, game["count"]))
        placement = 0

        for player_name, game_count, rating, delta in players:
            if player_name not in global_ratings:
                global_ratings[player_name] = []
            if player_name not in global_placements:
                global_placements[player_name] = []

            global_ratings[player_name].append((rating, game_count))

            # Only include placements in games where the player has played at least 3 matches
            if (game_count >= 3):
                # normalize placement to a number between 0 and 1, inclusive
                # To make it inclusive, subtract 1 from the length of the players list.
                # If the players list contains only one player, this would lead to
                # division by zero. But that shouldn't happen, right...?
                normalized_placement = placement / float(len(players) - 1)
                global_placements[player_name].append(
                    (normalized_placement, game_count))

            placement = placement + 1

    # Sort games on count (games played) descending
    games.sort(lambda game0, game1: game0[3] - game1[3], reverse=True)

    return render_template("index.html",
                           games=games,
                           top_list=top_list_placements(global_placements))


#                           top_list=top_list_ratings(global_ratings))


@app.route("/refresh/<name>")
def refresh(name):
    if refresh_from_game_file(name):
        return "done"
    else:
        abort(404)


@app.route("/refresh_game/<name>")
def refresh_game(name):
    if refresh_from_game_file(name):
        return redirect("/" + name)
    else:
        abort(404)


@app.route("/refresh_all")
def refresh_all():
    game_names = data.list()
    for name in game_names:
        refresh_from_game_file(name)
    return "done"


@app.route("/post_push", methods=["POST"])
def post_push():
    updated = {}
    data = request.form["payload"]
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
    abort(404)


@app.route("/<name>")
def show_game(name):
    try:
        game_data = data.load(name)
        return render_template("game.html",
                               name=name,
                               players=game_data["ratings"],
                               game_name=game_data["game_name"])
    except TypeError as te:
        logging.error(te)
        abort(404)


@app.route("/new", methods=["POST", "GET"])
@auth.required
def new_result():
    if request.method == "POST":
        return post_new_result()
    else:
        return get_new_result()


def get_new_result():
    games = map(lambda name: {
        'name': name,
        'game': data.load(name)
    }, sorted(data.list()))

    players_set = set()

    for game in games:
        players = game["game"]["ratings"]
        for player in players:
            name = player[0]
            players_set.add(name)

    players_list = list(players_set)
    players_list.sort()

    return render_template("new.html",
                           players=players_list,
                           games=games,
                           selected_game=request.args.get("game"))


def post_new_result():
    index = 0
    match = {
        "results": [],
        "time": strftime("%Y-%m-%d %H:%M"),
        "game": request.form.get("game")
    }

    for player in request.form.getlist("player"):
        score = request.form.getlist("score")[index]
        if player and score:
            match["results"].append((player, score))
        index += 1

    update_game(match)
    refresh_from_game_file(match["game"])

    return render_template("new_display.html", match=match)


def update_game(match):
    name = match["game"]
    try:
        content = get_game_file(name)

        if content == None:
            return False
        else:
            new_content = content + "\n"
            new_content += "game " + match["time"] + "\n"
            for (player, score) in match["results"]:
                new_content += player + " " + score + "\n"
            game_content.update(
                name + ".txt", new_content,
                "New game added by " + (request.current_user or "unkown") +
                " at " + strftime("%H:%M:%S"))
            return True
    except requests.HTTPError as e:
        logging.error(e)


if __name__ == "__main__":
    app.run(debug=True)
