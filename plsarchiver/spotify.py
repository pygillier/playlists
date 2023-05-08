import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
from flask import Flask, session


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

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        auth_manager = SpotifyOAuth(
            client_id=app.config["SPOTIFY_CLIENT_ID"],
            client_secret=app.config["SPOTIFY_CLIENT_SECRET"],
            redirect_uri="http://localhost:8082",
            scope=",".join(self.scopes),
            cache_handler=FlaskSessionCacheHandler(session)
        )
        self.client = spotipy.Spotify(auth_manager=auth_manager)

    def get_available_playlists(self):
        pls = self.client.current_user_playlists()
        return pls["items"]

    def get_liked_songs(self):
        return self.client.current_user_saved_tracks()

    def get_current_user(self):
        return self.client.current_user()

    def export_playlist(self, playlist_id: str):
        user = self.client.current_user()
        if not self.client.playlist_is_following(
                playlist_id=playlist_id,
                user_ids=[user["id"]]):
            return False

        pls = self.client.playlist_items(playlist_id=playlist_id)
        return list(map(reduce_exporter, pls["items"]))


client = SpotifyExtension()
