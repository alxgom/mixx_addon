import datetime
import dash
from dash import dcc, html, dash_table, no_update
import plotly.express as px
import pandas as pd
from src.database.database import get_tracks_for_playlist, format_duration, join_dates
from src.callbacks.shared import get_shared_data
from src.callbacks.plotly_template import register_swing_theme

register_swing_theme()  # register and set as default

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
            dash.Output("played-songs-table", "data"),
            dash.Output("artist-played-table", "data")
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

        # Assuming your DataFrame is called 'df' and the artist column is 'artist'
        df['standardized_artist'] = df['artist'].apply(standardize_artist_name)
        # Now you can group by the 'standardized_artist' column
        #artist_counts = df.groupby('standardized_artist').size().sort_values(ascending=False).head(10).reset_index(name='count')
        #print(artist_counts)
        #print("DataFrame head:\n", df.head())
        df["bpm"] = pd.to_numeric(df["bpm"], errors="coerce")
        df["duration"] = pd.to_numeric(df["duration"], errors="coerce")
    
        total_songs = len(df)
        unique_songs = len(df.drop_duplicates(subset=["artist", "album", "title"]))
        unique_artists = df["standardized_artist"].nunique()
        avg_bpm = df["bpm"].mean() if not df["bpm"].isna().all() else 0
        top_played_artist = df["standardized_artist"].value_counts().idxmax() if not df["standardized_artist"].isna().all() else "-"
    
        group_by_song = df.groupby(["standardized_artist", "title"]).size().reset_index(name="count")
        if not group_by_song.empty:
            top_song_row = group_by_song.sort_values("count", ascending=False).iloc[0]
            top_played_song = f"{top_song_row['standardized_artist']} – {top_song_row['title']} ({top_song_row['count']})"
        else:
            top_played_song = "-"
    
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
    
        total_songs_text = f"Total Songs: {total_songs}"
        unique_songs_text = f"Unique Songs: {unique_songs}"
        unique_artists_text = f"Unique Artists: {unique_artists}"
        avg_bpm_text = f"Avg BPM: {avg_bpm:.1f}"
        top_played_artist_text = f"Top Played Artist: {top_played_artist}"
        top_played_song_text = f"Top Played Song: {top_played_song}"
        avg_duration_text = f"Avg Duration: {avg_duration}"
        fastest_song_text = f"**Fastest Song:** {fastest_song}"
        slowest_song_text = f"**Slowest Song:** {slowest_song}"
    
        hist_fig = px.histogram(df, x="bpm", nbins=20, title="BPM Distribution")
        hist_fig.update_layout(xaxis_title="BPM", yaxis_title="Count")
    
        top_artists = df["standardized_artist"].value_counts().head(10).reset_index()
        top_artists.columns = ["standardized_artist", "count"]
 
        max_length = 15
        top_artists["short_artist"] = top_artists["standardized_artist"].apply(lambda x: x[:max_length] + "..." if len(x) > max_length else x)

        bar_fig = px.bar(top_artists, x="short_artist", y="count", title="Top 10 Artists",
                        color="count",  # <--- This is the key change!
                        color_continuous_scale=['#FFFDF8', '#CBA135'])  # Custom color scale                        hover_data={"standardized_artist": True, 'short_artist': False, 'count': True}) # Show full artist on hover
        bar_fig.update_layout(xaxis_title="", yaxis_title="Number of Songs",
                            xaxis_ticktext=top_artists["short_artist"],
                            xaxis_tickvals=top_artists["short_artist"])
        bar_fig.update_layout(coloraxis_cmax=top_artists['count'].max(),coloraxis_cmin=0,
                            coloraxis_showscale=False) # Set the minimum value for the color axis to 0
        
        box_fig = px.box(df, x="set_date", y="bpm", points="all", title="BPM Distribution by Set")
        box_fig.update_layout(xaxis_title="Set Date", yaxis_title="BPM")
    
        group_df = df.groupby(["standardized_artist", "title"]).agg(
            times_played=("title", "size"),
            dates=("set_date", join_dates),
            rating=("rating", "max")
        ).reset_index()
        group_df.rename(columns={'standardized_artist':"Artists","artist": "Artist", "title": "Song",
                                  "times_played": "Times Played", "dates": "Dates", "rating": "Rating"}, inplace=True)
        group_df = group_df[["Times Played", "Song", "Artists", "Dates", "Rating"]]
        
        played_songs_per_artist = df.groupby('standardized_artist')['title'].nunique().reset_index()
        played_songs_per_artist.rename(columns={'title': 'played_songs_per_artist'}, inplace=True)

        top_artists = df["standardized_artist"].value_counts().reset_index()
        top_artists.columns = ["standardized_artist", "count"]
        top_artists = top_artists.merge(played_songs_per_artist, on='standardized_artist', how='left')
        #group_by_song = df.groupby(["standardized_artist", "title"]).size().reset_index(name="count")
        #print(top_artists.head())
        # Assuming 'df' is your DataFrame with 'standardized_artist' and 'title' columns
        song_lists = df.groupby('standardized_artist')['title'].apply(lambda titles: ', '.join(sorted(set(titles)))).reset_index()
        song_lists.rename(columns={'title': 'song_list'}, inplace=True)
        # Merge the song lists with your top_artists DataFrame
        top_artists = top_artists.merge(song_lists, on='standardized_artist', how='left')

        tooltip_data = [
            {
                'standardized_artist': {'value': row['song_list'], 'type': 'text'}
            } for _, row in top_artists.iterrows()
        ]
        
        return (total_songs_text, unique_songs_text, unique_artists_text, avg_bpm_text,
                top_played_artist_text, top_played_song_text, avg_duration_text,
                fastest_song_text, slowest_song_text,
                hist_fig, bar_fig, box_fig,
                group_df.to_dict("records"),top_artists.to_dict("records"))
    
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

def standardize_artist_name(artist_string):
    """
    Standardizes artist names by splitting collaborations and returning a sorted,
    comma-separated string of individual artists.
    """
    separators = ["/", "|", "&"]
    artists = [artist_string]

    for sep in separators:
        new_artists = []
        for artist in artists:
            if sep in artist:
                new_artists.extend([a.strip() for a in artist.split(sep)])
            else:
                new_artists.append(artist)
        artists = new_artists

    # Further splitting by "feat." or "vs." if needed
    final_artists = []
    for artist in artists:
        if "feat." in artist:
            final_artists.extend([a.strip() for a in artist.split("feat.")])
        elif "vs." in artist:
            final_artists.extend([a.strip() for a in artist.split("vs.")])
        else:
            final_artists.append(artist)

    # Remove any empty strings and sort for consistency
    cleaned_artists = sorted([a for a in final_artists if a])
    return ", ".join(cleaned_artists)
