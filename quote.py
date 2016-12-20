import logging
import requests
import json
from random import randint
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session
from fuzzywuzzy import fuzz
from fuzzywuzzy import process


NUM_ROUNDS = 3
MAX_PLAYERS = 5

app = Flask(__name__)
ask = Ask(app, "/")

logger = logging.getLogger("flask_ask").setLevel(logging.DEBUG)


def get_new_quote():
    response = requests.post(
        "https://andruxnet-random-famous-quotes.p.mashape.com/?cat=movies",
        headers={
            "X-Mashape-Key": "qxw2noHOjgmshc3avMkLGu49Jcvrp186kqjjsnvnLClFDEYPGG",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
    )
    quote_json = json.loads(response.text)
    return quote_json


def check_response(provided, expected):
    return fuzz.ratio(provided.lower(), expected.lower())>=80


def current_player():
    return session.attributes.get('player', 1)


def current_round():
    return session.attributes.get('round', 1)


def number_of_players():
    return session.attributes.get('players', 1)


def score_for_player(player_num):
    score_key = "score_%d" % player_num
    return session.attributes.get(score_key, 0)


def set_score_for_player(player_num, score):
    score_key = "score_%d" % player_num
    session.attributes[score_key] = score


def get_scores():
    return [(n+1, score_for_player(n+1)) for n in range(number_of_players)]


def get_sorted_scores():
    def getkey(item):
        return item[1]
    return sorted(get_scores(), getkey)


def current_players_score():
    return score_for_player(current_player())


def increment_score():
    player_num = current_player()
    score = score_for_player(player_num)
    score += 1
    set_score_for_player(player_num, score)


def get_points_text(score):
    if score == 1:
        return "{0} point".format(score)
    elif score == 0:
        return "no points"
    else:
        return "{0} points".format(score)


def get_scores_text(scores=None):
    text = ''
    if scores is None:
        scores = get_sorted_scores()
    for (player_num, score) in scores:
        text += "{0} has {0}".format(
            get_player_text(player_num),
            get_points_text(score),
        )
    return text


def get_player_text(player_num):
    return "Player {0}".format(player_num)


def is_game_over():
    return session.attributes['round'] > NUM_ROUNDS


def increment_round():
    player_num = current_player()
    num_players = number_of_players()
    round_num = current_round()

    if player_num < num_players:
        player_num += 1
    else:
        player_num = 1
        round_num += 1

    session.attributes['round'] = round_num
    session.attributes['player'] = player_num


def setup_round():
    round_num = session.attributes.get('round', 1)
    player_num = session.attributes.get('player', 1)
    quote_json = get_new_quote()
    round_msg = render_template(
        'round',
        quote=quote_json['quote'],
        round=round_num,
        player_text=get_player_text(player_num),
    )
    session.attributes['quote_json'] = quote_json
    session.attributes['round_num'] = round_num
    return round_msg


@ask.launch
def new_game():
    welcome_msg = render_template('welcome')
    return question(welcome_msg)


@ask.intent("NumberOfPlayersIntent", convert={'players': int})
def number_of_players(players):
    logger.debug("Number of players: %s" % players)
    players_int = int(players)
    if players_int < 1:
        players_int = 1
    elif players_int >= MAX_PLAYERS:
        players_int = MAX_PLAYERS
    session.attributes['players'] = players_int
    round_message = setup_round()
    start_message = render_template(
        'game_start',
        rounds=NUM_ROUNDS,
    )
    msg = "%s %s" % (start_message, round_message)
    return question(msg)

#
# @ask.intent("YesIntent")
# def next_round():
#     msg = setup_round()
#     return question(msg)


@ask.intent("AnswerIntent")
def answer(author):
    quote_json = session.attributes.get('quote_json', None)
    if quote_json is None:
        return new_game()

    success = check_response(author, quote_json['author'])

    if success:
        increment_score()
        win_lose_message = render_template('win')
    else:
        win_lose_message = render_template('lose', author=quote_json['author'])

    increment_round()
    if is_game_over():
        # Show game over message and ask if they want to play again?
        sorted_scores = get_sorted_scores()
        winner = sorted_scores[0][0]
        winning_player_text = get_player_text(winner)
        game_over_message = render_template(
            'game_over',
            all_scores_text=get_scores_text(),
            winning_player_text=winning_player_text,
        )
        msg = "%s %s" % (win_lose_message, game_over_message)
        return statement(msg)
    else:
        # Show next round
        round_msg = setup_round()
        points_message = render_template('points',
                                         points_text=get_points_text())
        msg = "%s %s %s" % (win_lose_message, points_message, round_msg)
        return question(msg)

if __name__ == '__main__':
    app.run(debug=True)
