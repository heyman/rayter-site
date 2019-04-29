from flask import render_template, request, redirect, Response, abort
from pprint import pprint
from rayter.game_parser import GamesParser
from rayter.main import parse_file
from rayter.rater import Rater
from StringIO import StringIO
from time import strftime

import database
import games_data
import hashlib
import json
import numpy
import os.path
import requests
import settings
import urllib
import users_data
import logging
import achievements

def get_game_file(name):
    """
    Fetch game file.
    """
    return database.get_game(name + ".txt")


def refresh_from_game_file(name):
    """
    Fetch game file and re-calculate ratings. If the game file does not exist, the data will be deleted.
    """
    try:
        content = get_game_file(name)

        if content == None:
            games_data.delete(name)
            return False
        else:
            parser = GamesParser(StringIO(content), name)
            games = parser.parse_file()
            rater = Rater(games)
            ratings = rater.rate_games(parser.score_type)
            game = {
                "game_name": parser.game_name,
                "players": {
                    name: player.rating_history
                    for (name, player) in rater.players.items()
                },
                "ratings": ratings,
                "count": len(games),
            }
            games_data.save(name, game)
            return True
    except requests.HTTPError as e:
        logging.error(e)


def global_chart_ratings(ratings):
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


def global_chart_placements(placements):
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

    return average_placements


def get_new_result():
    games = map(lambda name: {
        'name': name,
        'game': games_data.load(name)
    }, sorted(games_data.list()))

    players_set = set()

    for game in games:
        players = game["game"]["ratings"]
        for player in players:
            name = player[0]
            players_set.add(name)

    players_list = list(players_set)
    players_list.sort()

    users = users_data.list_users()

    return render_template("new.html",
                           players=players_list,
                           games=games,
                           users=users,
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
            return "False"
        else:
            new_content = content + "\n"
            new_content += "game " + match["time"] + "\n"
            for (player, score) in match["results"]:
                new_content += player + " " + score + "\n"
            database.update_game(
                name + ".txt", new_content,
                "New game added by " + (request.current_user or "unkown") +
                " at " + strftime("%H:%M:%S"))
            return True
    except requests.HTTPError as e:
        logging.error(e)
        return False


def get_all_players():
    game_names = sorted(games_data.list())
    all_players = {}

    for name in game_names:
        game = games_data.load(name)
        players = game["ratings"]
        for player in players:
            user_name = player[0]
            all_players[user_name] = {"userName": user_name}

    return all_players


def make_image_url(user):
    # Don't override explicit imageUrl
    if 'imageUrl' in user:
        return user['imageUrl']

    size = 300
    fallbackImageUrl = 'https://api.adorable.io/avatars/' + str(
        size) + '/' + user['userName']

    if 'email' in user:
        email = user['email']
        hash = hashlib.md5(email.lower()).hexdigest()
        gravatar_url = "https://www.gravatar.com/avatar/" + hash + "?"
        gravatar_url += urllib.urlencode({
            's': str(size),
            'd': fallbackImageUrl
        })
        #    gravatar_url += urllib.urlencode({'d':default, 's':str(size)})
        return gravatar_url
    else:
        return fallbackImageUrl


def show_user(name):
    existing_user = users_data.load(name)
    user = existing_user or {"userName": name}

    game_names = sorted(games_data.list())
    ratings = []

    for game_name in game_names:
        game = games_data.load(game_name)
        players = game["ratings"]
        placement = 0
        for player_name, _0, rating, _1 in players:
            if player_name == name:
                ratings.append(
                    (game_name, game["game_name"], rating, placement))
            placement += 1

    ratings.sort(lambda (game0, game_name0, rating0, placement0), (
        game1, game_name1, rating1, placement1): int(rating0 - rating1),
                 reverse=True)

    # FIXME: (?)
    # All games are traversed twice, first in the loop above and then inside
    # get_games_and_toplist(), maybe they can be combined?
    (games, global_chart) = get_games_and_toplist()

    a = len(global_chart) >= 1 and global_chart[0][0] == name
    pprint(a)

    user_achievements = []

    if len(ratings) > 0:
        if ratings[0][2] > 2500:
            user_achievements.append(achievements.definitions['grand_master'])
        elif ratings[0][2] > 2000:
            user_achievements.append(achievements.definitions['master'])
        elif ratings[0][2] > 1500:
            user_achievements.append(achievements.definitions['journeyman'])
        elif ratings[0][2] > 1300:
            user_achievements.append(achievements.definitions['apprentice'])
        elif ratings[0][2] > 1100:
            user_achievements.append(achievements.definitions['challenger'])
        elif ratings[0][2] > 1000:
            user_achievements.append(achievements.definitions['not_bad'])
        if len(ratings) == 1:
            user_achievements.append(achievements.definitions['snowflake'])
        if ratings[0][2] > 1100 and ratings[-1][2] < 900:
            user_achievements.append(achievements.definitions['fluctuating'])
        if len(ratings) >= 3 and ratings[2][2] > 1100:
            user_achievements.append(achievements.definitions['diverse'])
        if len(ratings) >= 5 and ratings[-1][2] > 1100:
            user_achievements.append(achievements.definitions['star'])
        if len([placement for (game, game_name, rating, placement) in ratings if placement == 0]) > 0:
            user_achievements.append(achievements.definitions['number_one'])
        if len(global_chart) >= 1 and global_chart[0][0] == name:
            user_achievements.append(achievements.definitions['global_chart_gold'])
        if len(global_chart) >= 2 and global_chart[1][0] == name:
            user_achievements.append(achievements.definitions['global_chart_silver'])
        if len(global_chart) >= 3 and global_chart[2][0] == name:
            user_achievements.append(achievements.definitions['global_chart_bronze'])
        if len(ratings) >= 5:
            user_achievements.append(achievements.definitions['multi_player'])
        if len([player for (player, percent) in global_chart if player == name]) > 0:
            user_achievements.append(achievements.definitions['charter'])


    pprint(user_achievements)

    if len(ratings) > 0 or existing_user:
        return render_template("user.html", user=user, ratings=ratings, achievements=user_achievements)
    else:
        abort(404)


def refresh_users():
    all_players = get_all_players()
    try:
        # Fetch user JSON fron "database layer"
        users_json = database.get_metadata("users.json")

        if users_json == None:
            return "no json found"
        else:
            users_result = json.loads(users_json)
            users = users_result["users"]

            # Overwrite generic player values with user metadata
            for user in users:
                all_players[user["userName"]] = user

            # For every user, if she has no image add gravatar image or generated avatar
            for player in all_players:
                user = all_players[player]
                if not 'imageUrl' in user:
                    user['imageUrl'] = make_image_url(user)

            # Save users to redis
            users_data.save_users(all_players.values())
            return "done"
    except requests.HTTPError as e:
        logging.error(e)
        return "exception"


def show_game(name):
    try:
        game_data = games_data.load(name)
        users = users_data.list_users()

        return render_template("game.html",
                               name=name,
                               players=game_data["ratings"],
                               game_name=game_data["game_name"],
                               users=users)
    except TypeError as te:
        logging.error(te)
        abort(404)


def show_game_json(name):
    try:
        game_data = games_data.load(name)
        return Response(json.dumps(game_data), mimetype='application/json')
    except TypeError as te:
        logging.error(te)
        abort(404)


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


def refresh_all():
    game_names = games_data.list()
    for name in game_names:
        refresh_from_game_file(name)
    return "done"


def refresh_game(name):
    if refresh_from_game_file(name):
        return redirect("/" + name)
    else:
        abort(404)


def refresh(name):
    if refresh_from_game_file(name):
        return "done"
    else:
        abort(404)

def get_games_and_toplist():
    game_names = sorted(games_data.list())
    games = []
    global_placements = {}

    for name in game_names:
        game = games_data.load(name)
        players = game["ratings"]
        games.append((name, game["game_name"], players, game["count"]))
        placement = 0

        # Only include games with at least 3 players
        if len(players) >= 3:
            for player_name, game_count, rating, delta in players:
                if player_name not in global_placements:
                    global_placements[player_name] = []

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

    return (games, global_chart_placements(global_placements))

def index():
    (games, global_chart) = get_games_and_toplist()

    # Sort games on count (games played) descending
    games.sort(lambda (n0, gn0, p0, count0), (n1, gn1, p1, count1): count0 -
               count1,
               reverse=True)

    users = users_data.list_users()

    return render_template("index.html",
                           games=games,
                           users=users,
                           global_chart=global_chart)
