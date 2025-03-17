import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from src.database.database import get_library_songs
from src.callbacks.shared import party_set_options, playlist_id_to_date, default_start, default_end
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
        if "rating" in lib_df.columns and not lib_df.empty:
            rating_counts = lib_df["rating"].value_counts(dropna=False).reset_index()
            rating_counts.columns = ["rating", "count"]
            fig = px.pie(rating_counts, names="rating", values="count", title="Rating Distribution", hole=0.4)
        else:
            fig = {}
        lib_data = lib_df.to_dict("records")
        return total_text, fig, lib_data
