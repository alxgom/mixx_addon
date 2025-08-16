import dash
from dash import dcc, dash_table, html,ctx
import pandas as pd
from src.database.database import get_tracks_for_playlist, format_duration
from src.db import get_note, upsert_note
from datetime import datetime
import dash_bootstrap_components as dbc
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth,  SpotifyClientCredentials
import logging
import os

# Define the path where Render mounts the secret file
SECRET_FILE_PATH = '/etc/secrets/config.json'

# Check if the secret file exists (on Render)
if os.path.exists(SECRET_FILE_PATH):
    with open(SECRET_FILE_PATH, 'r') as f:
        config = json.load(f)
# Otherwise, fall back to the local file (for your computer)
else:
    with open('config.json', 'r') as f:
        config = json.load(f)

auth_manager = SpotifyClientCredentials(
    client_id=config['spotify']['client_id'],
    client_secret=config['spotify']['client_secret']
)
sp = spotipy.Spotify(auth_manager=auth_manager)

def export_mixxx_to_spotify(mixxx_playlist_id: int) -> str:
    """Export a Mixxx playlist to Spotify."""
    with open('config.json', 'r') as f:
        config = json.load(f)

    client_id = config['spotify']['client_id']
    client_secret = config['spotify']['client_secret']
    redirect_uri = config['spotify']['redirect_uri']
    username = config['spotify']['usr_name']

    scope = "playlist-read-private playlist-modify-public"
    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        username=username,
        scope=scope
    )
    sp = spotipy.Spotify(auth_manager=auth_manager)
    user_id = sp.me()['id']

    mixxx_tracks = get_tracks_for_playlist(mixxx_playlist_id)

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

    playlist_name = f"Mixxx Set {mixxx_playlist_id}"
    playlist = sp.user_playlist_create(
        user=user_id,
        name=playlist_name,
        public=True,
        description="Imported from Mixxx"
    )
    logging.info(f"Successfully created playlist: {playlist_name} with ID: {playlist['id']}")
    return playlist['id']


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
                track["bpm"] = round(float(track.get("bpm") or 0))
            except Exception:
                track["duration"] = "N/A"
                track["bpm"] = None
            track["play"] = "▶"
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
        df["bpm"] = pd.to_numeric(df["bpm"], errors="coerce").round(0).astype("Int64")
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
            return dbc.Alert("⚠️ Please select a playlist first.", color="warning", dismissable=True)

        try:
            url = export_mixxx_to_spotify(mixxx_playlist_id)
            return html.A("✅ Open in Spotify", href=url, target="_blank", style={"fontWeight": "bold"})
        except Exception as e:
            return dbc.Alert(f"❌ Error exporting: {e}", color="danger", dismissable=True)

    # New callback to load note and rating when playlist changes
    @app.callback(
        [dash.Output("playlist-note-textarea", "value"),
         dash.Output("playlist-note-rating", "value")],
        dash.Input("individual-playlist-dropdown", "value")
    )
    def load_playlist_note(playlist_id):
        if not playlist_id:
            return "", None
        note_text, rating = get_note(playlist_id)
        return note_text or "", rating

    @app.callback(
        dash.Output("save-note-alert", "children"),
        dash.Input("save-note-btn", "n_clicks"),
        dash.State("individual-playlist-dropdown", "value"),
        dash.State("playlist-note-textarea", "value"),
        dash.State("playlist-note-rating", "value"),
        prevent_initial_call=True
    )
    def save_note(n_clicks, playlist_id, notes, rating):
        if not playlist_id:
            return dbc.Alert("⚠️ No playlist selected.", color="warning", dismissable=True)

        upsert_note(playlist_id, notes, rating)
        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        alert_message = f"✅ Note saved successfully! Last modified: {now_str}"
        return dbc.Alert(alert_message, color="success", duration=4000, dismissable=True)

    @app.callback(
        dash.Output("spotify-player-iframe", "src"),
        dash.Input("individual-playlist-table", "active_cell"),
        dash.State("individual-playlist-table", "data"),
        prevent_initial_call=True
    )
    def play_track(active_cell, table_data):
        if not active_cell or active_cell["column_id"] != "play":
            raise dash.exceptions.PreventUpdate

        row = active_cell["row"]
        track = table_data[row]
        query = f"artist:{track['artist']} track:{track['title']}"

        results = sp.search(q=query, type="track", limit=1)
        items = results.get("tracks", {}).get("items", [])
        if not items:
            return ""  

        track_id = items[0]["id"]
        embed_url = f"https://open.spotify.com/embed/track/{track_id}"
        return embed_url
