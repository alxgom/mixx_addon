import dash
from dash import dcc, dash_table
import pandas as pd
from src.database.database import get_tracks_for_playlist, format_duration

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
