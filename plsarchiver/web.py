from flask import Flask, render_template
from plsarchiver.spotify import client
import datetime


def init_app(app: Flask):
    @app.route("/")
    def home():
        return render_template("index.html.j2")

    @app.route("/playlists")
    def playlists():
        user_playlists = client.get_available_playlists()
        user = client.get_current_user()
        return render_template("playlists.html.j2", playlists=user_playlists, user=user)

    @app.route("/likes")
    def likes():
        user_likes = client.get_liked_songs()
        user = client.get_current_user()
        return render_template("likes.html.j2", likes=user_likes["items"], user=user)

    @app.route("/export/<pls_id>")
    def export_playlist(pls_id: str):
        payload = client.export_playlist(playlist_id=pls_id)
        if payload is not False:
            return payload

    # Template filter for track duration
    @app.template_filter('duration')
    def human_duration(value):
        return datetime.timedelta(milliseconds=value)