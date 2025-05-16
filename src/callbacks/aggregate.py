import datetime
import dash
from dash import dcc, html, dash_table, no_update
import plotly.express as px
import pandas as pd
from src.database.database import get_tracks_for_playlist, format_duration, join_dates
from src.callbacks.shared import get_shared_data

def register_aggregate_callbacks(app):
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
            dash.Input("style-filter", "value"), 
            dash.Input("sets-dropdown", "value"),
            dash.Input("date-range-picker", "start_date"),
            dash.Input("date-range-picker", "end_date")
        ]
    )
    def update_aggregate_dashboard(styles, selected_set_ids, start_date, end_date):
        print("Aggregate callback triggered")
        shared = get_shared_data()
        # Get the up-to-date shared variables.
        playlist_id_to_date = shared["playlist_id_to_date"]
        party_sets = shared["party_sets"]

# ① Filter party_sets by selected style(s)
        valid_ids = []
        for pl in party_sets:
            parts = [p.strip().lower() for p in pl["name"].split(" - ")]
            style = parts[1] if len(parts) > 1 else ""
            if style in styles:
                valid_ids.append(pl["id"])

        # ② Intersect with user selection
        if not selected_set_ids:
            return _empty_aggregate()
        # keep only those selected that match style
        selected_set_ids = [pid for pid in selected_set_ids if pid in valid_ids]
        if not selected_set_ids:
            return _empty_aggregate()


        if not selected_set_ids:
            default_fig = {}
            return ("Total Songs: 0", "Unique Songs: 0", "Unique Artists: 0", "Avg BPM: 0",
                    "Top Played Artist: -", "Top Played Song: -", "Avg Duration: 0",
                    "Fastest Song: -", "Slowest Song: -",
                    default_fig, default_fig, default_fig, [])
    
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
        #print("Filtered playlist IDs:", filtered_set_ids)
        if not filtered_set_ids:
            default_fig = {}
            return ("Total Songs: 0", "Unique Songs: 0", "Unique Artists: 0", "Avg BPM: 0",
                    "Top Played Artist: -", "Top Played Song: -", "Avg Duration: 0",
                    "Fastest Song: -", "Slowest Song: -",
                    default_fig, default_fig, default_fig, [])
    
        all_tracks = []
        for set_id in filtered_set_ids:
            tracks = get_tracks_for_playlist(set_id)
            set_date = playlist_id_to_date.get(set_id)
            for track in tracks:
                track["set_date"] = set_date
                all_tracks.append(track)
        #print("Total tracks collected:", len(all_tracks))
        if not all_tracks:
            default_fig = {}
            return ("Total Songs: 0", "Unique Songs: 0", "Unique Artists: 0", "Avg BPM: 0",
                    "Top Played Artist: -", "Top Played Song: -", "Avg Duration: 0",
                    "Fastest Song: -", "Slowest Song: -",
                    default_fig, default_fig, default_fig, [])
    
        df = pd.DataFrame(all_tracks)
        #print("DataFrame head:\n", df.head())
        df["bpm"] = pd.to_numeric(df["bpm"], errors="coerce")
        df["duration"] = pd.to_numeric(df["duration"], errors="coerce")
    
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
    
        hist_fig = px.histogram(df, x="bpm", nbins=20, title="BPM Distribution")
        hist_fig.update_layout(xaxis_title="BPM", yaxis_title="Count")
    
        top_artists = df["artist"].value_counts().head(10).reset_index()
        top_artists.columns = ["artist", "count"]
        #bar_fig = px.bar(top_artists, x="artist", y="count", title="Top 10 Artists")
        #bar_fig.update_layout(xaxis_title="Artist", yaxis_title="Number of Songs")

        max_length = 15
        top_artists["short_artist"] = top_artists["artist"].apply(lambda x: x[:max_length] + "..." if len(x) > max_length else x)

        bar_fig = px.bar(top_artists, x="short_artist", y="count", title="Top 10 Artists",
                        hover_data={'artist': True, 'short_artist': False, 'count': True}) # Show full artist on hover
        bar_fig.update_layout(xaxis_title="Artist", yaxis_title="Number of Songs",
                            xaxis_ticktext=top_artists["short_artist"],
                            xaxis_tickvals=top_artists["short_artist"])

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
        # Use shared party_sets from fresh shared data.
        shared = get_shared_data()
        party_sets = shared["party_sets"]
        selected_ids = [pl["id"] for pl in party_sets if pl.get("date") and start_dt <= pl["date"] <= end_dt]
        return selected_ids
    
    global shared_data
    shared_data = {
        "party_set_options": get_shared_data()["party_set_options"],
        "playlist_id_to_date": get_shared_data()["playlist_id_to_date"],
        "default_start": get_shared_data()["default_start"],
        "default_end": get_shared_data()["default_end"]
    }
