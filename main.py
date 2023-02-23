import os
from io import StringIO

from jinja2 import Environment, FileSystemLoader
from rayter.game_parser import GamesParser
from rayter.rater import Rater



def get_template(name):
    env = Environment(loader=FileSystemLoader('templates'))
    return env.get_template(name)


def refresh_from_game_file(path, name):
    """
    Fetch game file and re-calculate ratings. If the game file does not exist, the data will be deleted.
    """
    with open(path, 'r') as f:
        content = f.read()

    parser = GamesParser(StringIO(content), name)
    games = parser.parse_file()
    rater = Rater(games)
    ratings = rater.rate_games(parser.score_type)

    game = {
        "slug": name,
        "game_name": parser.game_name,
        "players": {
            name: player.rating_history
            for (name, player) in list(rater.players.items())
        },
        "ratings": ratings,
        "count": len(games),
        "score_type": parser.score_type
    }

    return game


def render_game_page(game, base_path):
    filename = os.path.join(base_path, game['slug'], 'index.html')
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    print('Writing', filename)
    with open(filename, 'w') as f:
        f.write(get_template("game.html").render(
            name=game["game_name"],
            players=game["ratings"],
            game_name=game["game_name"],
            users=[],
        ))


def render_index_page(games, base_path):
    games.sort(key=lambda g: g["count"], reverse=True)
    with open(os.path.join(base_path, 'index.html'), 'w') as f:
        f.write(get_template("index.html").render(
            games=games,
            users=[],
            global_chart=[],
            log=[],
        ))

def main():
    games_path = '../rayter-games'
    output_path = "./output"

    games = []
    for filename in os.listdir(games_path):
        if not filename.endswith('.txt'):
            continue
        # remove .txt from filename
        name = filename[:-4]
        games.append(refresh_from_game_file(os.path.join(games_path, filename), name))

    # render game pages
    for game in games:
        render_game_page(game, output_path)

    # render index page
    render_index_page(games, output_path)


if __name__ == '__main__':
    main()
