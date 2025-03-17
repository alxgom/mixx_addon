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

# Precompute options and defaults based on playlists
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
    # -----------------------------
    # Render Tab Content Callback
    # -----------------------------
    @app.callback(
        dash.Output("tab-content", "children"),
        dash.Input("tabs", "active_tab")
    )
    def render_tab_content(active_tab):
        if active_tab == "aggregate":
            return html.Div([
                dbc.Row([
                    dbc.Col([
                        html.H5("Filters"),
                        dcc.Dropdown(
                            id="sets-dropdown",
                            options=party_set_options,
                            multi=True,
                            placeholder="Choose party sets",
                            style={"minHeight": "50px", "fontSize": "16px"}
                        ),
                        html.Br(),
                        dcc.DatePickerRange(
                            id="date-range-picker",
                            start_date=default_start,
                            end_date=default_end,
                            start_date_placeholder_text="Start Date",
                            end_date_placeholder_text="End Date",
                            style={"fontSize": "16px"}
                        )
                    ], width=12)
                ], style={"marginBottom": "20px"}),
                dbc.Row([
                    dbc.Col([
                        html.H5("Summary Metrics"),
                        dbc.Row([
                            dbc.Col(dbc.Card(html.H6(id="total-songs", children="Total Songs: 0"), body=True), width=4),
                            dbc.Col(dbc.Card(html.H6(id="unique-songs", children="Unique Songs: 0"), body=True), width=4),
                            dbc.Col(dbc.Card(html.H6(id="unique-artists", children="Unique Artists: 0"), body=True), width=4)
                        ], style={"marginBottom": "10px"}),
                        dbc.Row([
                            dbc.Col(dbc.Card(html.H6(id="avg-bpm", children="Avg BPM: 0"), body=True), width=4),
                            dbc.Col(dbc.Card(html.H6(id="top-played-artist", children="Top Played Artist: -"), body=True), width=4),
                            dbc.Col(dbc.Card(html.H6(id="top-played-song", children="Top Played Song: -"), body=True), width=4)
                        ], style={"marginBottom": "10px"}),
                        dbc.Row([
                            dbc.Col(dbc.Card(html.H6(id="avg-duration", children="Avg Duration: 0"), body=True), width=4),
                            dbc.Col(dbc.Card(html.H6(id="fastest-song", children="Fastest Song: -"), body=True), width=4),
                            dbc.Col(dbc.Card(html.H6(id="slowest-song", children="Slowest Song: -"), body=True), width=4)
                        ]),
                        dbc.Row([
                            dbc.Col(dbc.Card(html.H6(id="library-coverage", children="Library Coverage: 0 / 0 (0%)"), body=True), width=4)
                        ])
                    ], width=12)
                ], style={"marginBottom": "20px"}),
                dbc.Row([
                    dbc.Col(dcc.Graph(id="bpm-histogram"), width=6),
                    dbc.Col(dcc.Graph(id="artist-bar-chart"), width=6)
                ]),
                dbc.Row([
                    dbc.Col(dcc.Graph(id="bpm-boxplot"), width=12)
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col(
                        dash_table.DataTable(
                            id="played-songs-table",
                            columns=[
                                {"name": "Times Played", "id": "Times Played", "type": "numeric"},
                                {"name": "Song", "id": "Song"},
                                {"name": "Artist", "id": "Artist"},
                                {"name": "Dates", "id": "Dates"},
                                {"name": "Rating", "id": "Rating"}
                            ],
                            data=[],
                            sort_action="native",
                            page_size=40,
                            style_table={'overflowX': 'auto'},
                            style_cell={'textAlign': 'left', "fontSize": "14px"},
                            style_cell_conditional=[{'if': {'column_id': 'Artist'}, 'width': '80px'}]
                        ),
                        width=12
                    )
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col(
                        dash_table.DataTable(
                            id="artist-played-table",
                            columns=[
                                {"name": "Artist", "id": "Artist"},
                                {"name": "Times Played", "id": "Times Played", "type": "numeric"},
                                {"name": "Songs Count", "id": "Songs Count", "type": "numeric"}
                            ],
                            data=[],
                            sort_action="native",
                            page_size=40,
                            style_table={'overflowX': 'auto'},
                            style_cell={'textAlign': 'left', "fontSize": "14px"}
                        ),
                        width=12
                    )
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col(html.H5("Unplayed Artists"), width=12)
                ]),
                dbc.Row([
                    dbc.Col(
                        dash_table.DataTable(
                            id="unplayed-artists-table",
                            columns=[{"name": "Artist", "id": "Artist"}],
                            data=[],
                            sort_action="native",
                            page_size=40,
                            style_table={'overflowX': 'auto'},
                            style_cell={'textAlign': 'left', "fontSize": "14px"}
                        ),
                        width=12
                    )
                ])
            ])
        elif active_tab == "crates":
            return html.Div([
                html.H3("Crate Analysis"),
                dbc.Row([
                    dbc.Col(dash_table.DataTable(
                        id="detailed-crates-table",
                        columns=[
                            {"name": "Crate Name", "id": "name"},
                            {"name": "Total Songs", "id": "total_songs"}
                        ],
                        data=[],
                        style_table={'overflowX': 'auto'},
                        style_cell={'textAlign': 'left'}
                    ), width=12)
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col(dcc.Graph(id="crate-structure-chart"), width=12)
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col(
                        dash_table.DataTable(
                            id="crate-structure-table",
                            columns=[{"name": "Crate Path", "id": "Crate Path"}],
                            data=[],
                            sort_action="native",
                            page_size=40,
                            style_table={'overflowX': 'auto'},
                            style_cell={'textAlign': 'left', "fontSize": "14px"}
                        ),
                        width=12
                    )
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col(dcc.Graph(id="crate-bar-chart"), width=12)
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col(html.H5("Orphan Titles"), width=12)
                ]),
                dbc.Row([
                    dbc.Col(
                        dash_table.DataTable(
                            id="songs-without-crate-table",
                            columns=[
                                {"name": "Artist", "id": "artist"},
                                {"name": "Title", "id": "title"},
                                {"name": "Album", "id": "album"},
                                {"name": "BPM", "id": "bpm"},
                                {"name": "Duration", "id": "duration"},
                                {"name": "Rating", "id": "rating"}
                            ],
                            data=[],
                            sort_action="native",
                            page_size=40,
                            style_table={'overflowX': 'auto'},
                            style_cell={'textAlign': 'left', "fontSize": "14px"}
                        ),
                        width=12
                    )
                ])
            ])
        elif active_tab == "individual":
            return html.Div([
                html.H3("Individual Playlist Analysis"),
                dbc.Row([
                    dbc.Col([
                        html.Label("Select a Playlist:"),
                        dcc.Dropdown(
                            id="individual-playlist-dropdown",
                            options=party_set_options,
                            placeholder="Choose a playlist"
                        )
                    ], width=6)
                ], style={"marginBottom": "20px"}),
                dbc.Row([
                    dbc.Col(
                        dash_table.DataTable(
                            id="individual-playlist-table",
                            columns=[
                                {"name": "Artist", "id": "artist"},
                                {"name": "Title", "id": "title"},
                                {"name": "Album", "id": "album"},
                                {"name": "BPM", "id": "bpm"},
                                {"name": "Duration", "id": "duration"}
                            ],
                            data=[],
                            style_table={'overflowX': 'auto'},
                            style_cell={'textAlign': 'left'}
                        ),
                        width=12
                    )
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col(dcc.Graph(id="individual-playlist-cumulative-plot"), width=12)
                ])
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
                dbc.Row([
                    dbc.Col(dbc.Card(html.H6(id="library-total-songs", children="Total Songs: 0"), body=True), width=3)
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col(dcc.Graph(id="library-rating-distribution"), width=12)
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col(dash_table.DataTable(
                        id="library-table",
                        columns=columns,
                        data=lib_df.to_dict("records"),
                        sort_action="native",
                        page_size=40,
                        style_table={'overflowX': 'auto'},
                        style_cell={'textAlign': 'left', "fontSize": "14px"}
                    ), width=12)
                ])
            ])
        return html.Div("Tab not found")

    # -----------------------------
    # Aggregate Analysis Callback
    # -----------------------------
    @app.callback(
        [
            dash.Output("total-songs", "children"),
            dash.Output("unique-songs", "children"),
            dash.Output("unique-artists", "children"),
            dash.Output("avg-bpm", "children"),
            dash.Output("top-played-artist", "children"),
            dash.Output("top-played-song", "children"),
            dash.Output("avg-duration", "children"),
            dash.Output("fastest-song", "children"),
            dash.Output("slowest-song", "children"),
            dash.Output("bpm-histogram", "figure"),
            dash.Output("artist-bar-chart", "figure"),
            dash.Output("bpm-boxplot", "figure"),
            dash.Output("played-songs-table", "data")
        ],
        [
            dash.Input("sets-dropdown", "value"),
            dash.Input("date-range-picker", "start_date"),
            dash.Input("date-range-picker", "end_date")
        ]
    )
    def update_aggregate_dashboard(selected_set_ids, start_date, end_date):
        # Return defaults if no playlists are selected.
        if not selected_set_ids:
            default_fig = {}
            return ("Total Songs: 0", "Unique Songs: 0", "Unique Artists: 0", "Avg BPM: 0",
                    "Top Played Artist: -", "Top Played Song: -", "Avg Duration: 0",
                    "Fastest Song: -", "Slowest Song: -",
                    default_fig, default_fig, default_fig, [])
    
        start_date_dt = datetime.datetime.fromisoformat(start_date) if start_date else None
        end_date_dt = datetime.datetime.fromisoformat(end_date) if end_date else None
    
        # Filter playlists based on date range.
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
            default_fig = {}
            return ("Total Songs: 0", "Unique Songs: 0", "Unique Artists: 0", "Avg BPM: 0",
                    "Top Played Artist: -", "Top Played Song: -", "Avg Duration: 0",
                    "Fastest Song: -", "Slowest Song: -",
                    default_fig, default_fig, default_fig, [])
    
        # Gather all tracks from filtered playlists.
        all_tracks = []
        for set_id in filtered_set_ids:
            tracks = get_tracks_for_playlist(set_id)
            set_date = playlist_id_to_date.get(set_id)
            for track in tracks:
                track["set_date"] = set_date
                all_tracks.append(track)
    
        if not all_tracks:
            default_fig = {}
            return ("Total Songs: 0", "Unique Songs: 0", "Unique Artists: 0", "Avg BPM: 0",
                    "Top Played Artist: -", "Top Played Song: -", "Avg Duration: 0",
                    "Fastest Song: -", "Slowest Song: -",
                    default_fig, default_fig, default_fig, [])
    
        df = pd.DataFrame(all_tracks)
        df["bpm"] = pd.to_numeric(df["bpm"], errors="coerce")
        df["duration"] = pd.to_numeric(df["duration"], errors="coerce")
    
        # Compute summary metrics.
        total_songs = len(df)
        unique_songs = len(df.drop_duplicates(subset=["artist", "album", "title"]))
        unique_artists = df["artist"].nunique()
        avg_bpm = df["bpm"].mean() if not df["bpm"].isna().all() else 0
        top_played_artist = df["artist"].value_counts().idxmax() if not df["artist"].isna().all() else "-"
    
        group_by_song = df.groupby(["artist", "title"]).size().reset_index(name="count")
        if not group_by_song.empty:
            top_song_row = group_by_song.sort_values("count", ascending=False).iloc[0]
            top_played_song = f"{top_song_row['artist']} – {top_song_row['title']} ({top_song_row['count']})"
        else:
            top_played_song = "-"
    
        avg_duration_sec = df["duration"].mean() if not df["duration"].isna().all() else 0
        avg_duration = format_duration(avg_duration_sec)
    
        if not df["bpm"].isna().all():
            fastest_song_row = df.loc[df["bpm"].idxmax()]
            slowest_song_row = df.loc[df["bpm"].idxmin()]
            fastest_song = f"{fastest_song_row['artist']} – {fastest_song_row['title']} ({fastest_song_row['bpm']:.1f} BPM)"
            slowest_song = f"{slowest_song_row['artist']} – {slowest_song_row['title']} ({slowest_song_row['bpm']:.1f} BPM)"
        else:
            fastest_song = "-"
            slowest_song = "-"
    
        total_songs_text = f"Total Songs: {total_songs}"
        unique_songs_text = f"Unique Songs: {unique_songs}"
        unique_artists_text = f"Unique Artists: {unique_artists}"
        avg_bpm_text = f"Avg BPM: {avg_bpm:.1f}"
        top_played_artist_text = f"Top Played Artist: {top_played_artist}"
        top_played_song_text = f"Top Played Song: {top_played_song}"
        avg_duration_text = f"Avg Duration: {avg_duration}"
        fastest_song_text = f"Fastest Song: {fastest_song}"
        slowest_song_text = f"Slowest Song: {slowest_song}"
    
        # Build visualizations.
        hist_fig = px.histogram(df, x="bpm", nbins=20, title="BPM Distribution")
        hist_fig.update_layout(xaxis_title="BPM", yaxis_title="Count")
    
        top_artists = df["artist"].value_counts().head(10).reset_index()
        top_artists.columns = ["artist", "count"]
        bar_fig = px.bar(top_artists, x="artist", y="count", title="Top 10 Artists")
        bar_fig.update_layout(xaxis_title="Artist", yaxis_title="Number of Songs")
    
        box_fig = px.box(df, x="set_date", y="bpm", points="all", title="BPM Distribution by Set")
        box_fig.update_layout(xaxis_title="Set Date", yaxis_title="BPM", width=1200)
    
        group_df = df.groupby(["artist", "title"]).agg(
            times_played=("title", "size"),
            dates=("set_date", join_dates),
            rating=("rating", "max")
        ).reset_index()
        group_df.rename(columns={"artist": "Artist", "title": "Song",
                                  "times_played": "Times Played", "dates": "Dates", "rating": "Rating"}, inplace=True)
        group_df = group_df[["Times Played", "Song", "Artist", "Dates", "Rating"]]
    
        return (total_songs_text, unique_songs_text, unique_artists_text, avg_bpm_text,
                top_played_artist_text, top_played_song_text, avg_duration_text,
                fastest_song_text, slowest_song_text,
                hist_fig, bar_fig, box_fig,
                group_df.to_dict("records"))
    
    # -----------------------------
    # Callback for Individual Playlist Table
    # -----------------------------
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
    
    # -----------------------------
    # Callback for Individual Playlist Cumulative Plot
    # -----------------------------
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
    
    # -----------------------------
    # Callback for Artist Played Table
    # -----------------------------
    @app.callback(
        dash.Output("artist-played-table", "data"),
        [
            dash.Input("sets-dropdown", "value"),
            dash.Input("date-range-picker", "start_date"),
            dash.Input("date-range-picker", "end_date")
        ],
        allow_duplicate=True
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
    
    # -----------------------------
    # Callback for Library Tab Analytics
    # -----------------------------
    @app.callback(
        [
            dash.Output("library-total-songs", "children"),
            dash.Output("library-rating-distribution", "figure"),
            dash.Output("library-table", "data")
        ],
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
    
    @app.callback(
        dash.Output("sets-dropdown", "value"),
        [
            dash.Input("date-range-picker", "start_date"),
            dash.Input("date-range-picker", "end_date")
        ]
    )
    def update_sets_dropdown(start_date, end_date):
        if not start_date or not end_date:
            return no_update
        start_dt = datetime.datetime.fromisoformat(start_date)
        end_dt = datetime.datetime.fromisoformat(end_date)
        selected_ids = [pl["id"] for pl in party_sets if pl["date"] and start_dt <= pl["date"] <= end_dt]
        return selected_ids
