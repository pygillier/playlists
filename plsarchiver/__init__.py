from dotenv import load_dotenv
from flask import Flask
from flask_session import Session
from plsarchiver import web, spotify
import os

load_dotenv()

__version__ = "0.1.0"


def create_app(test_config=None):
    app = Flask(__name__)

    # Default configuration
    app.config.from_mapping(
        SESSION_COOKIE_SECURE=True,
        SESSION_TYPE="redis",
        SECRET_KEY="9e112ed7b89c58e9934d4c662152b31f0cb5776a8361a0e6293c146ca0107aaa",
        SPOTIFY_CLIENT_ID=os.getenv("SPOTIFY_CLIENT_ID"),
        SPOTIFY_CLIENT_SECRET=os.getenv("SPOTIFY_CLIENT_SECRET")
    )

    # Session
    sess = Session()
    sess.init_app(app)

    # Spotify extension
    from plsarchiver.spotify import client
    client.init_app(app)

    # App itself
    web.init_app(app)

    return app
