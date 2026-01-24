import dash
from dash import dcc, html, dash_table, no_update
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from src.database.database import get_crates, get_songs_not_in_crates, format_duration, get_songs_for_crate

def register_crates_callbacks(app):
    @app.callback(
        dash.Output("crate-structure-chart", "figure"),
        dash.Input("tabs", "active_tab")
    )
    def update_crate_structure_chart(active_tab):
        if active_tab != "crates":
            return no_update
        crates = get_crates()
        if not crates:
            return {}
        data = []
        max_levels = 0
        # Helper to check if a crate is a parent of another
        all_crate_parts = []
        for crate in crates:
            parts = [p.strip() for p in crate["name"].split("-") if p.strip()]
            all_crate_parts.append(parts)

        for crate in crates:
            parts = [p.strip() for p in crate["name"].split("-") if p.strip()]
            
            # Check if this crate is a prefix of any other crate
            is_parent = False
            for other_parts in all_crate_parts:
                if other_parts != parts and len(other_parts) > len(parts) and other_parts[:len(parts)] == parts:
                    is_parent = True
                    break
            
            # Only add leaf crates to the dataframe for sunburst
            # Plotly will infer parents automatically
            if not is_parent:
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
            return no_update, no_update
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

    @app.callback(
        dash.Output("crate-songs-table", "data"),
        dash.Input("crate-structure-chart", "clickData")
    )
    def update_crate_songs(clickData):
        if not clickData:
            return []
        
        point = clickData['points'][0]
        path = point.get('id')
        if not path:
             return []
        
        clicked_parts = path.split("/")
        
        crates = get_crates()
        target_crate_id = None
        
        for crate in crates:
            parts = [p.strip() for p in crate["name"].split("-") if p.strip()]
            if parts == clicked_parts:
                target_crate_id = crate['id']
                break
        
        if target_crate_id:
             songs = get_songs_for_crate(target_crate_id)
             if not songs:
                 return []
             df = pd.DataFrame(songs)
             df["bpm"] = pd.to_numeric(df["bpm"], errors="coerce")
             df["duration"] = pd.to_numeric(df["duration"], errors="coerce")
             df["duration"] = df["duration"].apply(lambda x: format_duration(x) if pd.notna(x) else "N/A")
             return df.to_dict("records")
        return []
