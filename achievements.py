def get_eligible_achievements(info):
    return [definition for definition in definitions if definition["eligible"](info)]

definitions = [
     # place 0 in global chart
    {
        "name": 'global_chart_gold',
        "eligible": lambda info: len(info["global_chart"]) >= 1 and info["global_chart"][0][0] == info["name"],
        'image': 'trophy',
        'name': 'Global #1',
        'text': 'Number one on the global chart'
    },
     # place 1 in global chart
    {
        "name": 'global_chart_silver',
        "eligible": lambda info: len(info["global_chart"]) >= 2 and info["global_chart"][1][0] == info["name"],
        'image': 'medal',
        'name': 'Global #2',
        'text': 'Number two on the global chart'
    },
     # place 2 in global chart
    {
        "name": 'global_chart_bronze',
        "eligible": lambda info: len(info["global_chart"]) >= 3 and info["global_chart"][2][0] == info["name"],
        'image': 'award',
        'name': 'Global #3',
        'text': 'Number three on the global chart'
    },
    # played at least 5 games, all ratings above 1100
    {
        "name": 'star',
        "eligible": lambda info: len(info["ratings"]) >= 5 and info["ratings"][-1][2] > 1100,
        'image': 'star',
        'name': 'Star',
        'text': 'Played at least five games and all ratings above 1100'
    },
    # leader in at least one game
    {
        "name": 'number_one',
        "eligible": lambda info: len([placement for (game, game_name, rating, placement) in info["ratings"] if placement == 0]) > 0,
        'image': 'crown',
        'name': 'Number One',
        'text': 'Leader of at least one game'
    },
    # at least three ratings > 1100
    {
        "name": 'diverse',
        "eligible": lambda info: len(info["ratings"]) >= 3 and info["ratings"][2][2] > 1100,
        'image': 'hand-peace',
        'name': 'Diverse',
        'text': 'Rating above 1100 in at least three games'
    },
    # highest rating > 2500
    {
        "name": 'grand_master',
        "eligible": lambda info: info["ratings"][0][2] > 2500,
        'image': 'hat-wizard',
        'name': 'Grand Master',
        'text': 'At least one rating above 2500'
    },
    # highest rating > 2000
    {
        "name": 'master',
        "eligible": lambda info: info["ratings"][0][2] > 2000,
        'image': 'gem',
        'name': 'Master',
        'text': 'At least one rating above 2000'
    },
    # highest rating > 1500
    {
        "name": 'journeyman',
        "eligible": lambda info: info["ratings"][0][2] > 1500,
        'image': 'hammer',
        'name': 'Journeyman',
        'text': 'At least one rating above 1500'
    },
    # highest rating > 1300
    {
        "name": 'apprentice',
        "eligible": lambda info: info["ratings"][0][2] > 1300,
        'image': 'broom',
        'name': 'Apprentice',
        'text': 'At least one rating above 1300'
    },
    # highest rating > 1100
    {
        "name": 'challenger',
        "eligible": lambda info: info["ratings"][0][2] > 1100,
        'image': 'rocket',
        'name': 'Challenger',
        'text': 'At least one rating above 1100'
    },
    # highest rating > 1000
    {
        "name": 'not_bad',
        "eligible": lambda info: info["ratings"][0][2] > 1000,
        'image': 'thumbs-up',
        'name': "Not bad!",
        'text': 'At least one rating above 1000.'
    },
     # Low highest rating :)
    {
        "name": 'potential',
        "eligible": lambda info: info["ratings"][0][2] <= 1000,
        'image': 'level-up-alt',
        'name': 'Potential',
        'text': 'Has real potential to improve rating!'
    },
     # on global chart
    {
        "name": 'charter',
        "eligible": lambda info: len([player for (player, percent) in info["global_chart"] if player == info["name"]]) > 0,
        'image': 'list-ol',
        'name': 'Charter',
        'text': 'Member of the global chart'
    },
     # played all games
    {
        "name": 'versatile',
        "eligible": lambda info: len(info["ratings"]) == len(info["games"]),
        'image': 'asterisk',
        'name': 'Versatile',
        'text': 'Played all games'
    },
    # only played one type of game
    {
        "name": 'snowflake',
        "eligible": lambda info: len(info["ratings"]) == 1,
        'image': 'snowflake',
        'name': 'Snowflake',
        'text': 'Only played one kind of game'
    },
    # highest rating > 1100 and lowest rating < 900
    {
        "name": 'fluctuating',
        "eligible": lambda info: info["ratings"][0][2] > 1100 and info["ratings"][-1][2] < 900,
        'image': 'arrows-alt-v',
        'name': 'Fluctuating',
        'text': 'At least one rating above 1100 and at least one rating below 900'
    },
     # Played at least 5 different types of games
    {
        "name": 'multi_player',
        "eligible": lambda info: len(info["ratings"]) >= 5,
        'image': 'headset',
        'name': 'Multi Player',
        'text': 'Played at least five different types of games'
    },
]
