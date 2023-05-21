from dotenv import load_dotenv
from flask import Flask
from flask_session import Session
from flask_caching import Cache
from flask_bootstrap import Bootstrap5
from flask_debugtoolbar import DebugToolbarExtension
from plsarchiver import web
import os
import logging
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration


load_dotenv()

__version__ = "0.1.0"

# Cache
cache = Cache()


def create_app(config=None):
    app = Flask(__name__)

    # Load configuration
    current_env = config if config is not None else os.getenv("FLASK_ENV")
    app.config.from_object(f"plsarchiver.settings.{current_env}")

    # Eager prod configuration for services & logs
    if config == "prod":
        # Reuse gunicorn logging
        gunicorn_logger = logging.getLogger('gunicorn.error')
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)

        # Setup Sentry
        sentry_sdk.init(
            dsn="",
            integrations=[FlaskIntegration()]
        )

    app.logger.info(f"Loaded {current_env} configuration")

    if app.config["DEBUG"] is True:
        toolbar = DebugToolbarExtension(app)

    # Session
    sess = Session()
    sess.init_app(app)
    app.logger.debug("Session init")

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
