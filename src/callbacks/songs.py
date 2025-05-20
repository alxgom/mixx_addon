import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from src.database.database import get_library_songs
import json
from urllib.parse import quote


def register_songs_callbacks(app):
    @app.callback(
        [dash.Output("library-total-songs", "children"),
         dash.Output("library-rating-distribution", "figure"),
         dash.Output("library-table", "data")],
        dash.Input("tabs", "active_tab")
    )
    return