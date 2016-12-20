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
    else:
        return "{0} points".format(score)


@ask.launch
def new_game():

    welcome_msg = render_template('welcome')
    session.attributes['round']=1
    return question(welcome_msg)


@ask.intent("YesIntent")
def next_round():
    quote_json = get_new_quote()
    round_msg = render_template('round', quote=quote_json['quote'],
                                round=session.attributes['round'])

    session.attributes['quote_json'] = quote_json
    return question(round_msg)


@ask.intent("AnswerIntent", convert={'first': int, 'second': int, 'third': int})
def answer(author):
    quote_json = session.attributes.get('quote_json', None)
    if quote_json is None:
        return new_game()

    if check_response(author, quote_json['author']):
        increment_score()
        msg = render_template(
            'win',
            points_text=get_points_text()
        )
    else:
        msg = render_template(
            'lose',
            author=quote_json['author'],
            points_text=get_points_text()
        )
    return question(msg)


@ask.intent("ContinueIntent")
def continue_round():   
    session.attributes['round'] = session.attributes['round'] + 1
    if session.attributes['round'] <= NUM_ROUNDS:
        return next_round()
    else:
        msg = render_template('end')
        return statement(msg)

if __name__ == '__main__':
    app.run(debug=True)
