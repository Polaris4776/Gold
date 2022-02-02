from flask import Flask
from threading import Thread

APP = Flask("")


@APP.route("/")
def home():
    return "Bot is online"


def run():
    APP.run(host='0.0.0.0', port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()
