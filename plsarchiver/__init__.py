from dotenv import load_dotenv
from flask import Flask
from flask_session import Session
from flask_caching import Cache
from flask_bootstrap import Bootstrap5
from plsarchiver import web
import os

load_dotenv()

__version__ = "0.1.0"

# Cache
cache = Cache()


def create_app(test_config=None):
    app = Flask(__name__)

    # Default configuration
    app.config.from_mapping(
        SESSION_COOKIE_SECURE=True,
        SESSION_TYPE="redis",
        SECRET_KEY="9e112ed7b89c58e9934d4c662152b31f0cb5776a8361a0e6293c146ca0107aaa",
        SPOTIFY_CLIENT_ID=os.getenv("SPOTIFY_CLIENT_ID"),
        SPOTIFY_CLIENT_SECRET=os.getenv("SPOTIFY_CLIENT_SECRET"),
        CACHE_TYPE="RedisCache",
        CACHE_REDIS_URL=os.getenv("REDIS_URL", "redis://redis:6379/0")
    )

    # Session
    sess = Session()
    sess.init_app(app)

    # Cache
    cache.init_app(app)

    # Bootstrap
    bootstrap = Bootstrap5(app=app)

    # Spotify extension
    from plsarchiver.spotify import client
    client.init_app(app)

    # App itself
    web.init_app(app)

    return app
