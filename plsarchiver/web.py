from flask import Flask, render_template, Response, request, session, redirect
from plsarchiver.spotify import client
from plsarchiver.m3u import M3U
from plsarchiver import forms
from plsarchiver.decorators import login_required
from dateutil.parser import parse
from werkzeug.exceptions import HTTPException

import datetime
import timeago
import json


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
    @login_required
    def likes():
        name, user_likes = client.get_liked_songs()
        # Metrics
        duration = 0
        oldest = None
        youngest = None
        for track in user_likes:
            duration += track["track"]["duration_ms"]
            track_added_at = parse(track["added_at"], ignoretz=True)
            # Oldest & youngest
            if oldest is None:
                oldest = track_added_at
            else:
                oldest = track_added_at if track_added_at < oldest else oldest

            if youngest is None:
                youngest = track_added_at
            else:
                youngest = track_added_at if track_added_at > youngest else youngest

        return render_template("likes.html.j2",
                               likes=user_likes,
                               user=client.user,
                               duration=duration,
                               oldest=oldest,
                               convert_form=forms.ConvertLikesToPlsForm(),
                               youngest=youngest)

    @app.route("/convert")
    def convert_likes():
        playlist = client.create_playlist_from_liked_songs(
            playlist_name="{}: Liked Songs".format(datetime.datetime.now().strftime("%Y-%m-%d"))
        )
        return render_template("convert.html.j2", playlist=playlist)

    @app.route("/export/<pls_id>")
    def export_playlist(pls_id: str):
        if pls_id != "likes":
            (name, payload) = client.export_playlist(playlist_id=pls_id)
        else:
            (name, payload) = client.get_liked_songs()

        user = client.current_user

        return Response(
            M3U.convert(payload),
            mimetype='text/plain',
            headers={'Content-disposition': f"attachment; filename={user['id']}-liked-songs.m3u8"})

    @app.route("/oauth_dance")
    def handle_oauth():
        # Do we have a code ?
        if request.args.get("code"):
            client.get_access_token(token=request.args.get("code"))
            redirect_uri = session["login_redirect_uri"] if "login_redirect_uri" in session else "/"
            return redirect(redirect_uri)
        else:
            return redirect("/")

    @app.route("/forget")
    def forget_me():
        session.clear()
        return redirect("/")

    @app.errorhandler(HTTPException)
    def handle_exception(e):
        """Return JSON instead of HTML for HTTP errors."""
        # start with the correct headers and status code from the error
        response = e.get_response()
        # replace the body with JSON
        response.data = json.dumps({
            "code": e.code,
            "name": e.name,
            "description": e.description,
        })
        response.content_type = "application/json"
        return response

    # Template filter for track duration
    @app.template_filter('duration')
    def human_duration(value):
        d = datetime.timedelta(milliseconds=value)
        seconds = int(d.total_seconds())
        periods = [
            ('year',        60*60*24*365),
            ('month',       60*60*24*30),
            ('day',         60*60*24),
            ('hour',        60*60),
            ('minute',      60),
            ('second',      1)
        ]

        strings = []
        for period_name, period_seconds in periods:
            if seconds > period_seconds:
                period_value , seconds = divmod(seconds, period_seconds)
                has_s = 's' if period_value > 1 else ''
                strings.append("%s %s%s" % (period_value, period_name, has_s))

        return ", ".join(strings)

    @app.template_filter('timeago')
    def from_now(date):
        return timeago.format(date, datetime.datetime.now())
