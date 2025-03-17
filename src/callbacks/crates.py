import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from src.database.database import get_crates, get_songs_not_in_crates, format_duration
from src.callbacks.shared import party_set_options, playlist_id_to_date, default_start, default_end
def register_crates_callbacks(app):
    @app.callback(
        dash.Output("crate-structure-chart", "figure"),
        dash.Input("tabs", "active_tab")
    )
    def update_crate_structure_chart(active_tab):
        if active_tab != "crates":
            return dash.no_update
        crates = get_crates()
        if not crates:
            return {}
        data = []
        max_levels = 0
        for crate in crates:
            parts = [p.strip() for p in crate["name"].split("-") if p.strip()]
            max_levels = max(max_levels, len(parts))
            row = {f"level{i+1}": part for i, part in enumerate(parts)}
            data.append(row)
        for row in data:
            for i in range(len(row) + 1, max_levels + 1):
                row[f"level{i}"] = None
        df = pd.DataFrame(data)
        level_cols = [f"level{i+1}" for i in range(max_levels)]
        fig = px.sunburst(df, path=level_cols, values=None, title="Crate Hierarchical Structure")
        fig.update_layout(width=1400, height=800)
        return fig

    @app.callback(
        [dash.Output("crate-structure-table", "data"),
         dash.Output("crate-structure-table", "columns")],
        dash.Input("tabs", "active_tab")
    )
    def update_crate_structure_table(active_tab):
        if active_tab != "crates":
            return dash.no_update, dash.no_update
        crates = get_crates()
        if not crates:
            return [], []
        data = []
        for crate in crates:
            parts = [p.strip() for p in crate["name"].split("-") if p.strip()]
            path = " / ".join(parts)
            data.append({"Crate Path": path})
        columns = [{"name": "Crate Path", "id": "Crate Path"}]
        return data, columns

    @app.callback(
        dash.Output("songs-without-crate-table", "data"),
        dash.Input("tabs", "active_tab")
    )
    def update_songs_without_crate_table(active_tab):
        if active_tab != "crates":
            return []
        songs = get_songs_not_in_crates()
        if not songs:
            return []
        df = pd.DataFrame(songs)
        df["bpm"] = pd.to_numeric(df["bpm"], errors="coerce")
        df["duration"] = pd.to_numeric(df["duration"], errors="coerce")
        df["duration"] = df["duration"].apply(lambda x: format_duration(x) if pd.notna(x) else "N/A")
        df = df.sort_values("artist")
        return df.to_dict("records")
