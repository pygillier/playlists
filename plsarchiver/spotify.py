from typing import Any
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
from flask import Flask, session, current_app


def reduce_exporter(item):
    entries_to_pop = [
        "added_at",
        "added_by",
        "is_local",
        "primary_color",
        "video_thumbnail"
    ]
    for entry in entries_to_pop:
        item.pop(entry)

    return item


class SpotifyExtension:

    client: spotipy.Spotify
    scopes = ["playlist-read-private",
              "playlist-modify-private",
              "playlist-modify-public",
              "user-library-read"]
    current_user = None
    cache_handler: FlaskSessionCacheHandler
    auth_manager: SpotifyOAuth

    def __init__(self, app=None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        self.cache_handler = FlaskSessionCacheHandler(session)

        self.auth_manager = SpotifyOAuth(
            client_id=app.config["SPOTIFY_CLIENT_ID"],
            client_secret=app.config["SPOTIFY_CLIENT_SECRET"],
            redirect_uri=f"{app.config['SPOTIFY_REDIRECT_URI']}/oauth_dance",
            scope=",".join(self.scopes),
            cache_handler=self.cache_handler
        )

        self.client = spotipy.Spotify(auth_manager=self.auth_manager)

    def is_logged_in(self):
        return self.auth_manager.validate_token(self.cache_handler.get_cached_token())

    def get_authorize_url(self):
        return self.auth_manager.get_authorize_url()

    def get_access_token(self, token: str) -> None:
        self.auth_manager.get_access_token(code=token)

    @property
    def user(self) -> list:
        if self.current_user is None:
            self.current_user = self.client.current_user()
        return self.current_user

    def get_available_playlists(self) -> dict:
        pls = self.client.current_user_playlists()
        return pls["items"]

    def get_liked_songs(self, limit=50, use_cache=True) -> tuple[str, list]:
        from . import cache  # noqa
        offset = 0
        songs = []
        songs_len = 1

        cache_key = "{}:likes".format(self.user["uri"])

        if use_cache and cache.has(cache_key):
            current_app.logger.warning(f"Loading cache key {cache_key}")
            return "likes", cache.get(cache_key)

        while songs_len != 0:
            current_app.logger.info(f"Fetching likes from {offset} with a {limit} limit - Current len is {songs_len}")
            results = self.client.current_user_saved_tracks(offset=offset, limit=limit)
            songs += results["items"]

            # Loop control
            offset = limit + offset
            songs_len = len(results["items"])

        if use_cache:
            cache.set(cache_key, songs)
        return "likes", songs

    def export_playlist(self, playlist_id: str) -> list | bool:
        if not self.client.playlist_is_following(
                playlist_id=playlist_id,
                user_ids=[self.user["id"]]):
            return False

        pls = self.client.playlist_items(playlist_id=playlist_id)
        return list(map(reduce_exporter, pls["items"]))

    def create_playlist_from_liked_songs(self, playlist_name: str) -> Any:
        n, likes = self.get_liked_songs()
        uris = [t["track"]["uri"] for t in likes]

        playlist = self.client.user_playlist_create(
            user=self.user["id"],
            name=playlist_name,
            public=False,
            collaborative=False,
            description="Export from Liked Songs"
        )
        self.client.playlist_add_items(
            playlist_id=playlist["id"],
            items=uris
        )
        return playlist


client = SpotifyExtension()
