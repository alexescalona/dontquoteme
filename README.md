# dontquoteme
Fun Alexa hackathon project.

## Quick start

### Set up virtual environment using Python virtualenv

    virtualenv /path/to/env
    . /path/to/env/bin/activate
    
### Install project dependencies

    pip install -r requirements.txt

### Run locally

    python memory_game.py

### Deploy to AWS

* Add credentials group called "nni_hackathon" in `~/.aws/credentials`
* Deploy with `zappa`:

      zappa deploy dev

## Resources & references

* Flask, a Python web framework
* [Flask Ask](https://github.com/johnwheeler/flask-ask), a Flask library for creating Alexa skills 
  * [AWS Blog post outlining using Flask Ask](https://developer.amazon.com/blogs/post/Tx14R0IYYGH3SKT/Flask-Ask-A-New-Python-Framework-for-Rapid-Alexa-Skills-Kit-Development)
* [Zappa](https://github.com/Miserlou/Zappa), a Python library for deploying web applications to AWS Lambda
