import logging
import requests
import json
from random import randint
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session


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
    quote_json = session.attributes['quote_json']
    if author == quote_json['author']:
        msg = render_template('win')
    else:
        msg = render_template('lose', author=quote_json['author'])
    return question(msg)


@ask.intent("ContinueIntent")
def continue_round():   
    session.attributes['round'] = session.attributes['round'] + 1
    if session.attributes['round'] < 3:
        return next_round()
    else:
        msg = render_template('end')
        return statement(msg)

if __name__ == '__main__':
    app.run(debug=True)



# import requests
# #https://andruxnet-random-famous-quotes.p.mashape.com/?cat=famous
# # These code snippets use an open-source library. http://unirest.io/python
# response = requests.post("https://andruxnet-random-famous-quotes.p.mashape.com/?cat=movies",
#   headers={
#     "X-Mashape-Key": "qxw2noHOjgmshc3avMkLGu49Jcvrp186kqjjsnvnLClFDEYPGG",
#     "Content-Type": "application/x-www-form-urlencoded",
#     "Accept": "application/json"
#   }
# )
# print response