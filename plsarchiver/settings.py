import os
from dotenv import load_dotenv
from redis import Redis

load_dotenv()


class Config:
    TESTING = False
    SECRET_KEY = os.getenv("SECRET_KEY")

    # Cache config
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_HOST = "cache"
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_DB = 0

    # Session config
    SESSION_COOKIE_SECURE = True
    SESSION_TYPE = "redis"
    SESSION_REDIS = Redis(host=CACHE_REDIS_HOST, port=CACHE_REDIS_PORT, db=CACHE_REDIS_DB)

    # Spotify config
    SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")


class DevelopmentConfig(Config):
    DEBUG = True
    CACHE_REDIS_HOST = "localhost"


class ProductionConfig(Config):
    SENTRY_DSN = os.getenv("SENTRY_DSN")


# mappings
development = DevelopmentConfig()
prod = ProductionConfig()
