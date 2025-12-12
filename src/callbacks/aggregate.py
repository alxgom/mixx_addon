import datetime
import dash
#from dash import dcc, html, dash_table, no_update
import plotly.express as px
import pandas as pd
from src.database.database import get_tracks_for_playlist, format_duration, join_dates
from src.callbacks.shared import get_shared_data, clean_and_split_artists
from src.callbacks.plotly_template import register_swing_theme


register_swing_theme()  # register and set as default


def register_aggregate_callbacks(app):

    @app.callback(
        [
            dash.Output("total-songs", "children"),
            dash.Output("total-blues-sets", "children"),
            dash.Output("total-lindy-sets", "children"),
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
            dash.Output("repetition-plot", "figure"),
            dash.Output("played-songs-table", "data"),
            dash.Output("artist-played-table", "data"),
            dash.Output("unplayed-artists-table", "data")
        ],
        [
            dash.Input("style-filter", "value"), 
            dash.Input("sets-dropdown", "value"),
            dash.Input("date-range-picker", "start_date"),
            dash.Input("date-range-picker", "end_date")
        ]
    )
    def update_aggregate_dashboard(styles, selected_set_ids, start_date, end_date):
        shared = get_shared_data()
        playlist_id_to_date = shared["playlist_id_to_date"]
        party_sets = shared["party_sets"]
        repetition_stats = shared.get("repetition_stats", [])

        # Filter by styles
        valid_ids = []
        for pl in party_sets:
            parts = [p.strip().lower() for p in pl["name"].split(" - ")]
            style = parts[1] if len(parts) > 1 else ""
            if style in styles:
                valid_ids.append(pl["id"])

        if not selected_set_ids:
            return _empty_aggregate()
        selected_set_ids = [pid for pid in selected_set_ids if pid in valid_ids]
        if not selected_set_ids:
            return _empty_aggregate()

        # Filter by date range
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
            return _empty_aggregate()

        # Collect all tracks
        all_tracks = []
        for set_id in filtered_set_ids:
            tracks = get_tracks_for_playlist(set_id)
            set_date = playlist_id_to_date.get(set_id)
            for track in tracks:
                track["set_date"] = set_date
                all_tracks.append(track)
        if not all_tracks:
            return _empty_aggregate()

        df = pd.DataFrame(all_tracks)
        df["bpm"] = pd.to_numeric(df["bpm"], errors="coerce")
        df["duration"] = pd.to_numeric(df["duration"], errors="coerce")

        # === EXPLODE ARTISTS ===
       
        df['artist_list'] = df['artist'].apply(clean_and_split_artists)
        df_exploded = df.explode('artist_list')

        df_exploded = df_exploded[df_exploded["artist_list"].notna() & (df_exploded["artist_list"] != "")]


        # === STATISTICS ===
        total_songs = len(df)
        unique_songs = len(df.drop_duplicates(subset=["artist", "album", "title"]))
        unique_artists = df_exploded["artist_list"].nunique()
        avg_bpm = df_exploded["bpm"].mean() if not df_exploded["bpm"].isna().all() else 0

        # Style Counts
        blues_count = 0
        lindy_count = 0
        for pid in filtered_set_ids:
             # Find name from matching set in party_sets
             # We can't easily look up by ID from the list without iterating? 
             # Or we can build a temporary lookup
             pl = next((p for p in party_sets if p["id"] == pid), None)
             if pl:
                 parts = [p.strip().lower() for p in pl["name"].split(" - ")]
                 style = parts[1] if len(parts) > 1 else ""
                 if style == "blues":
                     blues_count += 1
                 elif style == "lindy":
                     lindy_count += 1

        # Top played artist (by track count)
        top_played_artist = df_exploded["artist_list"].value_counts().idxmax() if not df_exploded["artist_list"].isna().all() else "-"

        # Top played song
        group_by_song = df.groupby(["artist", "title"]).size().reset_index(name="count")
        if not group_by_song.empty:
            top_song_row = group_by_song.sort_values("count", ascending=False).iloc[0]
            top_played_song = f"{top_song_row['artist']} – {top_song_row['title']} ({top_song_row['count']})"
        else:
            top_played_song = "-"

        # Duration
        avg_duration_sec = df["duration"].mean() if not df["duration"].isna().all() else 0
        avg_duration = format_duration(avg_duration_sec)

        if not df["bpm"].isna().all():
            fastest_song_row = df.loc[df["bpm"].idxmax()]
            slowest_song_row = df.loc[df["bpm"].idxmin()]  
            fastest_song = f"({fastest_song_row['bpm']:.1f} BPM)  \n *{fastest_song_row['title']}*  \n {fastest_song_row['artist']}   "
            slowest_song = f"({slowest_song_row['bpm']:.1f} BPM)  \n *{slowest_song_row['title']}*  \n {slowest_song_row['artist']} "
        else:
            fastest_song = "-"
            slowest_song = "-"

        # === HISTOGRAM ===
        hist_fig = px.histogram(df_exploded, x="bpm", nbins=20, title="BPM Distribution")
        hist_fig.update_layout(xaxis_title="BPM", yaxis_title="Count",xaxis_range=[30, None] )

        # === TOP ARTISTS BAR PLOT ===
        top_artists = df_exploded['artist_list'].value_counts().head(10).reset_index()
        top_artists.columns = ["artist_list", "count"]
        bar_fig = px.bar(top_artists, x="artist_list", y="count", title="Top 10 Artists",
                         color="count", color_continuous_scale=['#FFFDF8', '#CBA135'])
        bar_fig.update_layout(xaxis_title="", yaxis_title="Number of Songs",
                              coloraxis_showscale=False)

        # === BPM BOX PLOT ===
        box_fig = px.box(df_exploded, x="set_date", y="bpm", points="all", title="BPM Distribution by Set")
        box_fig.update_layout(xaxis_title="Set Date", yaxis_title="BPM")

        # === REPETITION PLOT ===
        # Filter repetition stats to selected sets
        rep_df = pd.DataFrame(repetition_stats)
        if not rep_df.empty:
            # We filter by ID using the same logic as the main filter
            rep_df = rep_df[rep_df["id"].isin(filtered_set_ids)]
            
            # Format Date for Tooltip
            if not rep_df.empty:
                 rep_df["date_str"] = rep_df["date"].apply(lambda d: d.strftime('%d-%m-%Y') if d else "")

            # Melt for multiple lines
            rep_melted = rep_df.melt(id_vars=["date", "date_str", "name"], 
                                     value_vars=["pct_first", "pct_second", "pct_third_plus"],
                                     var_name="Category", value_name="Percentage")
            
            category_map = {
                "pct_first": "First Time",
                "pct_second": "Second Time",
                "pct_third_plus": "3+ Times"
            }
            rep_melted["Category"] = rep_melted["Category"].map(category_map)
            
            # Create a sequential order column for the x-axis to avoid time gaps
            # We want the order to be based on the set dates/sequence
            # rep_melted contains 3 rows per set. We need to assign the same order to each trio.
            # Using rank or dense_rank on date is one way, or just mapping id to an index.
            
            # Get unique dates/ids sorted
            unique_sets = rep_melted[["date", "id"] if "id" in rep_melted.columns else ["date", "name"]].drop_duplicates().sort_values("date")
            unique_sets["Set Order"] = range(1, len(unique_sets) + 1)
            
            # Merge back to get the order
            rep_melted = rep_melted.merge(unique_sets[["date", "Set Order"]], on="date", how="left")

            rep_fig = px.line(rep_melted, x="Set Order", y="Percentage", color="Category",
                              title="Song First-Time & Repetition Stats",
                              hover_data=["name", "date_str"], 
                              markers=True,
                              symbol="Category",   # Different markers
                              line_dash="Category" # Different line styles
                              )
            
            rep_fig.update_traces(
                line=dict(width=3), 
                marker=dict(size=8),
                hovertemplate="<b>%{customdata[0]}</b><br>Date: %{customdata[1]}<br>Set Order: %{x}<br>Percentage: %{y:.0f}%<extra></extra>"
            ) 
            rep_fig.update_layout(xaxis_title="Set Sequence (Order)", yaxis_title="Percentage (%)", yaxis_range=[0, 100])
        else:
            rep_fig = {}

        # === PLAYED SONGS TABLE ===
        played_songs_table = df.groupby(["artist", "title"]).agg(
            times_played=("title", "size"),
            dates=("set_date", join_dates),
            rating=("rating", "max")
        ).reset_index()
        played_songs_table.rename(columns={
            "artist": "Artists",
            "title": "Song",
            "times_played": "Times Played",
            "dates": "Dates",
            "rating": "Rating"
        }, inplace=True)
        played_songs_table = played_songs_table[["Times Played", "Song", "Artists", "Dates", "Rating"]]

        # === TOP ARTISTS TABLE ===
        artist_counts = df_exploded.groupby('artist_list').agg(
            count=('title', 'size'),
            played_songs_per_artist=('title', 'nunique')
        ).reset_index()
        artist_counts.rename(columns={'artist_list': 'Artists'}, inplace=True)

        # === UNPLAYED ARTISTS ===
        all_library_artists = shared.get("all_library_artists", set())
        played_artists = set(df_exploded['artist_list'].unique())
        unplayed_artists = sorted(all_library_artists - played_artists)
        unplayed_artists_table = [{"Artists": a} for a in unplayed_artists]

        # Return all outputs
        return (
            f"Total Songs: {total_songs}",
            f"Blues Sets: {blues_count}",
            f"Lindy Sets: {lindy_count}",
            f"Unique Songs: {unique_songs}",
            f"Unique Artists: {unique_artists}",
            f"Avg BPM: {avg_bpm:.1f}",
            f"Top Played Artist: {top_played_artist}",
            f"Top Played Song: {top_played_song}",
            f"Avg Duration: {avg_duration}",
            f"Fastest Song: {fastest_song}",
            f"Slowest Song: {slowest_song}",
            hist_fig,
            bar_fig,
            box_fig,
            rep_fig,
            played_songs_table.to_dict('records'),
            artist_counts.to_dict('records'),
            unplayed_artists_table
        )

def _empty_aggregate():
    """Return empty placeholders for aggregate callback."""
    default_fig = {}
    return ("Total Songs: 0", "Blues Sets: 0", "Lindy Sets: 0", "Unique Songs: 0", "Unique Artists: 0", "Avg BPM: 0",
            "Top Played Artist: -", "Top Played Song: -", "Avg Duration: 0",
            "-", "-", default_fig, default_fig, default_fig, default_fig, [], [], [])
    
    
    
    
    
    '''
            

    import re
import pandas as pd
from dash import Input, Output, State, dash_table
import plotly.express as px
# --- Helper function to clean & split artist names ---


def register_aggregate_callbacks(app):
    # --- Callback for updating artist analysis ---
    @app.callback(
        Output("artist-bar-chart", "figure"),
        Output("artist-played-table", "data"),
        Output("top-played-artist", "children"),
        Output("unplayed-artists-table", "data"),
        Input("playlist-store", "data"),
        State("master-artist-list-store", "data")
    )
    def update_artist_analysis(playlist_data, master_artist_list):
        if not playlist_data:
            return px.bar(), [], "Top Played Artist: -", []

        df = pd.DataFrame(playlist_data)

        # Explode artists into separate rows
        df_exploded = df.assign(
            artist_list=df["standardized_artist"].apply(clean_and_split_artists)
        ).explode("artist_list")

        # Remove any empty values
        df_exploded = df_exploded[df_exploded["artist_list"].notna() & (df_exploded["artist_list"] != "")]

        # Count plays per artist
        artist_counts = (
            df_exploded.groupby("artist_list")
            .agg(count=("artist_list", "size"),
                played_songs_per_artist=("Track Name", "nunique"))
            .reset_index()
            .rename(columns={"artist_list": "standardized_artist"})
            .sort_values(by="count", ascending=False)
        )

        # Bar chart
        fig = px.bar(
            artist_counts.head(20),
            x="standardized_artist",
            y="count",
            title="Top Played Artists",
            labels={"standardized_artist": "Artist", "count": "Times Played"}
        )
        fig.update_layout(xaxis_tickangle=-45)

        # Top artist name
        top_artist_name = artist_counts.iloc[0]["standardized_artist"] if not artist_counts.empty else "-"
        top_artist_text = f"Top Played Artist: {top_artist_name}"

        # Unplayed artists
        if master_artist_list:
            cleaned_master_list = []
            for a in master_artist_list:
                cleaned_master_list.extend(clean_and_split_artists(a))
            cleaned_master_list = sorted(set(cleaned_master_list))

            played_artists_set = set(artist_counts["standardized_artist"])
            unplayed_artists = [{"Artists": a} for a in cleaned_master_list if a not in played_artists_set]
        else:
            unplayed_artists = []

        return fig, artist_counts.to_dict("records"), top_artist_text, unplayed_artists


            '''