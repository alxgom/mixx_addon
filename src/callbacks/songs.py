import dash
from dash import dcc, html, dash_table, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
from src.database.database import get_library_songs


def register_songs_callbacks(app):

    @app.callback(
        # Output('results-table', 'data'),
        Input('search-input', 'value')
    )
    def update_table(search_value):
        library_songs = get_library_songs()
        lib_df = pd.DataFrame(library_songs) if library_songs else pd.DataFrame()

        if not search_value:
            return []

        search_value = search_value.lower()

        filtered_df = lib_df[
            lib_df['title'].str.lower().str.contains(search_value) |
            lib_df['artist'].str.lower().str.contains(search_value)
        ]

        return filtered_df.to_dict('records')

    # **Do NOT return anything from this function itself!**
