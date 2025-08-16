import dash
#from dash import dcc, html, dash_table
#import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from src.database.database import get_library_songs

def register_library_callbacks(app):
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
        
        # Process ratings: convert to numeric, drop songs without rating and filter for ratings 1 to 5.
        if "rating" in lib_df.columns and not lib_df.empty:
            lib_df["rating"] = pd.to_numeric(lib_df["rating"], errors="coerce")
            rated_df = lib_df.dropna(subset=["rating"])
            rated_df = rated_df[(rated_df["rating"] >= 1) & (rated_df["rating"] <= 5)]
            rating_counts = rated_df["rating"].value_counts().sort_index().reset_index()
            rating_counts.columns = ["rating", "count"]
            fig = px.bar(rating_counts, x="rating", y="count", title="Song Ratings Distribution (1-5)")
            fig.update_layout(xaxis_title="Rating", yaxis_title="Number of Songs")
        else:
            fig = {}
        lib_data = lib_df.to_dict("records")
        return total_text, fig, lib_data
