import spotipy
from spotipy.oauth2 import SpotifyPKCE


class PLSClient:

    client: spotipy.Spotify
    scopes = ["playlist-read-private",
              "playlist-modify-private",
              "playlist-modify-public"]

    def __init__(self, client_id: str):
        auth_manager = SpotifyPKCE(
            client_id=client_id,
            redirect_uri="http://localhost:8082",
            scope=",".join(self.scopes)
        )
        self.client = spotipy.Spotify(auth_manager=auth_manager)

    def playlists(self):
       playlists = self.client.current_user_playlists()

       editable_pls = filter(PLSClient.filter_pls, playlists["items"])
       print(editable_pls)

    @staticmethod
    def filter_pls(p):
        return not p["public"]
