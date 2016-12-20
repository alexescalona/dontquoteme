import logging
import requests
import json
from random import randint
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session
from fuzzywuzzy import fuzz
from fuzzywuzzy import process


NUM_ROUNDS = 3


app = Flask(__name__)
ask = Ask(app, "/")

logging.getLogger("flask_ask").setLevel(logging.DEBUG)


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


def increment_score():
    score = session.attributes.get('score', 0)
    score += 1
    session.attributes['score'] = score


def get_points_text():
    score = session.attributes.get('score', 0)
    if score == 1:
        return "{0} point".format(score)
    elif score == 0:
        return "no points"
    else:
        return "{0} points".format(score)


def is_game_over():
    return session.attributes['round'] > NUM_ROUNDS


def increment_round():
    round_num = session.attributes.get('round', 1)
    round_num += 1
    session.attributes['round'] = round_num


def setup_round():
    round_num = session.attributes.get('round', 1)
    quote_json = get_new_quote()
    round_msg = render_template(
        'round',
        quote=quote_json['quote'],
        round=round_num,
    )
    session.attributes['quote_json'] = quote_json
    session.attributes['round_num'] = round_num
    return round_msg


@ask.launch
def new_game():
    welcome_msg = render_template('welcome')
    return question(welcome_msg)


@ask.intent("YesIntent")
def next_round():
    msg = setup_round()
    return question(msg)


@ask.intent("AnswerIntent", convert={'first': int, 'second': int, 'third': int})
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
        game_over_message = render_template(
            'game_over',
            points_text=get_points_text()
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
