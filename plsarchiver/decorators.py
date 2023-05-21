from functools import wraps
from flask import redirect, request, session
from plsarchiver.spotify import client


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not client.is_logged_in():
            session["login_redirect_uri"] = request.path
            return redirect(client.get_authorize_url())
        return f(*args, **kwargs)
    return decorated_function
