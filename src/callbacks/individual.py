import dash
from dash import dcc, dash_table
import pandas as pd
from src.database.database import get_tracks_for_playlist, format_duration

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials


def export_mixxx_to_spotify(mixxx_playlist_id: int) -> str:
    """
    Export a Mixxx playlist to Spotify.

    Args:
      mixxx_playlist_id: the Mixxx playlist ID (from your SQLite query).
      spotify_username: your Spotify username / user ID.

    Returns:
      The URL of the newly created Spotify playlist.
    """
    # 1) Authenticate to Spotify (scopes for private playlist creation & modify)

    client_credentials = SpotifyClientCredentials(
    client_id="a6bb815b933c4d7f8dfc16b138bfe72f",
    client_secret="78a4f53693f34885b87f4cf208c8c4fc"
    )
    # Set your desired scopes
    SCOPE = (
        "playlist-read-private "
        "playlist-modify-public "
        "playlist-modify-private"
    )
    sp = Spotify(auth_manager=client_credentials)
        # SpotifyOAuth will read CLIENT_ID, CLIENT_SECRET, REDIRECT_URI from env by default
    

    # 2) Fetch tracks from Mixxx
    mixxx_tracks = get_tracks_for_playlist(mixxx_playlist_id)

    # 3) Search Spotify for each track
    track_uris = []
    for track in mixxx_tracks:
        artist = track.get("artist", "").strip()
        title = track.get("title", "").strip()
        if not artist or not title:
            continue
        query = f"artist:{artist} track:{title}"
        res = sp.search(q=query, type="track", limit=1)
        items = res.get("tracks", {}).get("items", [])
        if items:
            track_uris.append(items[0]["uri"])

    # 4) Create a new private playlist named after your Mixxx set
    #    (you could also embed the date or original name here)
    playlist_name = f"Mixxx Set {mixxx_playlist_id}"
    playlist = sp.user_playlist_create(
        user="11127699528",
        name=playlist_name,
        public=True,
        description="Imported from Mixxx"
    )

    # 5) Add tracks to the new playlist in batches of 100
    for i in range(0, len(track_uris), 100):
        batch = track_uris[i:i+100]
        sp.playlist_add_items(playlist_id=playlist["id"], items=batch)

    return playlist["external_urls"]["spotify"]


def register_individual_callbacks(app):
    @app.callback(
        dash.Output("individual-playlist-table", "data"),
        dash.Input("individual-playlist-dropdown", "value")
    )
    def update_individual_playlist(selected_playlist):
        if not selected_playlist:
            return []
        tracks = get_tracks_for_playlist(selected_playlist)
        for track in tracks:
            try:
                track["duration"] = format_duration(track.get("duration"))
            except Exception:
                track["duration"] = "N/A"
        return tracks

    @app.callback(
        dash.Output("individual-playlist-cumulative-plot", "figure"),
        dash.Input("individual-playlist-dropdown", "value")
    )
    def update_individual_playlist_plot(selected_playlist):
        if not selected_playlist:
            return {}
        tracks = get_tracks_for_playlist(selected_playlist)
        if not tracks:
            return {}
        df = pd.DataFrame(tracks)
        df["bpm"] = pd.to_numeric(df["bpm"], errors="coerce")
        df["duration"] = pd.to_numeric(df["duration"], errors="coerce")
        df = df.sort_values("position")
        df["cumulative_time"] = df["duration"].cumsum() / 60.0
        total_duration = df["duration"].sum() / 60.0
        title_text = f"BPM vs. Cumulative Elapsed Time (Total Duration: {total_duration:.1f} min)"
        import plotly.express as px
        fig = px.line(
            df,
            x="cumulative_time",
            y="bpm",
            markers=True,
            title=title_text,
            hover_data={
                "title": True,
                "artist": True,
                "rating": True,
                "bpm": True,
                "duration": False,
                "cumulative_time": False
            }
        )
        fig.update_layout(xaxis_title="Elapsed Time (minutes)", yaxis_title="BPM")
        return fig

    @app.callback(
        dash.Output("export-spotify-link", "children"),
        dash.Input("export-spotify-btn", "n_clicks"),
        dash.State("individual-playlist-dropdown", "value"),
        prevent_initial_call=True
    )
    def on_export(n_clicks, mixxx_playlist_id):
        if not mixxx_playlist_id:
            return "Please select a playlist first."
        try:
            url = export_mixxx_to_spotify(mixxx_playlist_id)
            print(href=url)
            return html.A("Open in Spotify", href=url, target="_blank")
        except Exception as e:
            return f"Error exporting: {e}"