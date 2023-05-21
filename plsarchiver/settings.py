import os
from datetime import timedelta
from dotenv import load_dotenv
from redis import Redis

load_dotenv()


class Config:
    TESTING = False
    SECRET_KEY = os.getenv("SECRET_KEY")

    # Cache config
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = "redis://cache:6379/0"

    # Session config
    SESSION_COOKIE_SECURE = True
    SESSION_TYPE = "redis"
    SESSION_REDIS = Redis(host="cache", port=6379, db=0)
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=300)

    # Spotify config
    SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
    SPOTIFY_REDIRECT_URI = "http://localhost:5000"

    # Debug toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False


class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    CACHE_REDIS_URL = "redis://localhost:6379/0"
    SESSION_REDIS = Redis(host="localhost", port=6379, db=0)


class ProductionConfig(Config):
    SENTRY_DSN = os.getenv("SENTRY_DSN")
    SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)


# mappings
development = DevelopmentConfig()
prod = ProductionConfig()
