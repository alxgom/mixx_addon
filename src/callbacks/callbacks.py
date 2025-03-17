import datetime
import dash
from dash import dcc, html, dash_table, no_update
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

from src.database.database import (
    get_playlists,
    get_tracks_for_playlist,
    get_crates,
    get_songs_not_in_crates,
    get_library_songs,
    format_duration,
    join_dates
)

# Precompute options and defaults
all_playlists = get_playlists()
party_sets = [pl for pl in all_playlists if pl["date"] is not None]
playlist_id_to_date = {pl["id"]: pl["date"] for pl in party_sets}
party_set_options = sorted(
    [{"label": pl["name"], "value": pl["id"]} for pl in party_sets],
    key=lambda x: playlist_id_to_date[x["value"]]
)
if party_sets:
    earliest_date = min(pl["date"] for pl in party_sets if pl["date"] is not None)
    default_start = earliest_date.date().isoformat()
else:
    default_start = None
default_end = datetime.datetime.now().date().isoformat()

def register_callbacks(app):
    @app.callback(
        dash.Output("tab-content", "children"),
        dash.Input("tabs", "active_tab")
    )
    def render_tab_content(active_tab):
        if active_tab == "aggregate":
            return html.Div([
                # Replace with your complete Aggregate layout
                html.Div("Aggregate Layout..."),
            ])
        elif active_tab == "crates":
            return html.Div([
                html.H3("Crate Analysis"),
                html.Div("Crate Analysis Layout...")
            ])
        elif active_tab == "individual":
            return html.Div([
                html.H3("Individual Playlist Analysis"),
                dcc.Dropdown(
                    id="individual-playlist-dropdown",
                    options=party_set_options,
                    placeholder="Choose a playlist"
                ),
                dash_table.DataTable(
                    id="individual-playlist-table",
                    columns=[
                        {"name": "Artist", "id": "artist"},
                        {"name": "Title", "id": "title"},
                        {"name": "Album", "id": "album"},
                        {"name": "BPM", "id": "bpm"},
                        {"name": "Duration", "id": "duration"}
                    ],
                    data=[]
                ),
                dcc.Graph(id="individual-playlist-cumulative-plot")
            ])
        elif active_tab == "library":
            library_songs = get_library_songs()
            lib_df = pd.DataFrame(library_songs) if library_songs else pd.DataFrame()
            columns = [
                {"name": "ID", "id": "id"},
                {"name": "Artist", "id": "artist"},
                {"name": "Title", "id": "title"},
                {"name": "Album", "id": "album"},
                {"name": "Rating", "id": "rating"}
            ]
            return html.Div([
                html.H3("Library Data"),
                dbc.Card(html.H6(id="library-total-songs", children="Total Songs: 0")),
                dcc.Graph(id="library-rating-distribution"),
                dash_table.DataTable(
                    id="library-table",
                    columns=columns,
                    data=lib_df.to_dict("records")
                )
            ])
        return html.Div("Tab not found")

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
        dash.Output("artist-played-table", "data"),
        [
            dash.Input("sets-dropdown", "value"),
            dash.Input("date-range-picker", "start_date"),
            dash.Input("date-range-picker", "end_date")
        ]
    )
    def update_artist_played_table(selected_set_ids, start_date, end_date):
        if not selected_set_ids:
            return []
        start_date_dt = datetime.datetime.fromisoformat(start_date) if start_date else None
        end_date_dt = datetime.datetime.fromisoformat(end_date) if end_date else None
        filtered_set_ids = []
        for set_id in selected_set_ids:
            set_date = playlist_id_to_date.get(set_id)
            if set_date:
                if start_date_dt and set_date < start_date_dt:
                    continue
                if end_date_dt and set_date > end_date_dt:
                    continue
                filtered_set_ids.append(set_id)
        if not filtered_set_ids:
            return []
        all_tracks = []
        for set_id in filtered_set_ids:
            tracks = get_tracks_for_playlist(set_id)
            set_date = playlist_id_to_date.get(set_id)
            for track in tracks:
                track["set_date"] = set_date
                all_tracks.append(track)
        if not all_tracks:
            return []
        df = pd.DataFrame(all_tracks)
        df["bpm"] = pd.to_numeric(df["bpm"], errors="coerce")
        df["duration"] = pd.to_numeric(df["duration"], errors="coerce")
        artist_group = df.groupby("artist").agg(
            times_played=("artist", "size"),
            songs_count=("title", "nunique")
        ).reset_index()
        artist_group.rename(columns={"artist": "Artist", "times_played": "Times Played", "songs_count": "Songs Count"}, inplace=True)
        artist_group = artist_group.sort_values("Times Played", ascending=False)
        return artist_group.to_dict("records")

    @app.callback(
        [dash.Output("library-total-songs", "children"),
         dash.Output("library-rating-distribution", "figure"),
         dash.Output("library-table", "data")],
        dash.Input("tabs", "active_tab")
    )
    def update_library_tab(active_tab):
        if active_tab != "library":
            raise dash.exceptions.PreventUpdate
        library_songs = get_library_songs()
        lib_df = pd.DataFrame(library_songs) if library_songs else pd.DataFrame()
        total = len(lib_df)
        total_text = f"Total Songs: {total}"
        if "rating" in lib_df.columns and not lib_df.empty:
            rating_counts = lib_df["rating"].value_counts(dropna=False).reset_index()
            rating_counts.columns = ["rating", "count"]
            fig = px.pie(rating_counts, names="rating", values="count", title="Rating Distribution", hole=0.4)
        else:
            fig = {}
        lib_data = lib_df.to_dict("records")
        return total_text, fig, lib_data

    # (Insert your aggregate analysis callback here as needed)
