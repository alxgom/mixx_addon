import dash
from dash import dcc, html, dash_table, no_update
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from src.database.database import get_crates, get_songs_not_in_crates, format_duration, get_songs_for_crate, get_crate_counts, get_all_crates_summary

def register_crates_callbacks(app):
    @app.callback(
        dash.Output("crate-structure-chart", "figure"),
        [
            dash.Input("tabs", "active_tab"),
            dash.Input("chart-type-toggle", "value")
        ]
    )
    def update_crate_structure_chart(active_tab, chart_type):
        if active_tab != "crates":
            return no_update
        crates = get_crates()
        if not crates:
            return {}
            
        counts = get_crate_counts()
        
        # We need to build all unique nodes, because users might not have explicitly created the parent crate.
        # E.g. they have "Swing - Fast" but never created "Swing" alone.
        all_paths = set()
        for crate in crates:
            parts = [p.strip() for p in crate["name"].split("-") if p.strip()]
            for i in range(1, len(parts) + 1):
                all_paths.add("/".join(parts[:i]))
                
        all_paths = sorted(list(all_paths))
        
        # Calculate cumulative songs per path
        path_counts = {}
        for path in all_paths:
            total = 0
            for crate in crates:
                crate_parts = [p.strip() for p in crate["name"].split("-") if p.strip()]
                crate_path = "/".join(crate_parts)
                if crate_path == path or crate_path.startswith(path + "/"):
                    total += counts.get(crate['id'], 0)
            path_counts[path] = total

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
        
        if chart_type == "icicle":
            fig = px.icicle(df, path=level_cols, values=None, title="Crate Hierarchical Structure")
        else:
            fig = px.sunburst(df, path=level_cols, values=None, title="Crate Hierarchical Structure")
        
        # Inject custom hover text mappings
        if fig.data:
            trace = fig.data[0]
            custom_hover = []
            for path_id in trace.ids:
                if path_id in path_counts:
                    custom_hover.append(f"{path_counts[path_id]} songs")
                else:
                    custom_hover.append("")
            
            trace.customdata = custom_hover
            trace.hovertemplate = "<b>%{label}</b><br>%{customdata}<extra></extra>"
            if chart_type == "icicle":
                trace.tiling = dict(orientation='h')
                trace.textinfo = "label"
                trace.textfont = dict(size=13)
            
        fig.update_layout(margin=dict(t=40, l=0, r=0, b=0))
        return fig

    @app.callback(
        dash.Output("crate-structure-table", "data"),
        dash.Input("tabs", "active_tab")
    )
    def update_crate_structure_table(active_tab):
        if active_tab != "crates":
            return no_update
            
        summaries = get_all_crates_summary()
        if not summaries:
            return []
            
        data = []
        for row in summaries:
            parts = [p.strip() for p in row["name"].split("-") if p.strip()]
            path = " / ".join(parts)
            
            data.append({
                "Crate Path": path,
                "Total Songs": row.get("total_songs", 0)
            })
            
        # Sort alphabetically by path
        data.sort(key=lambda x: x["Crate Path"])
        return data

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
        df["bpm"] = df["bpm"].fillna(0)
        df["duration"] = pd.to_numeric(df["duration"], errors="coerce")
        df["duration"] = df["duration"].apply(lambda x: format_duration(x) if pd.notna(x) else "N/A")
        df = df.sort_values("artist")
        return df.to_dict("records")

    @app.callback(
        dash.Output("crate-songs-table", "data"),
        [
            dash.Input("crate-structure-chart", "clickData"),
            dash.Input("crate-structure-table", "selected_rows")
        ],
        [dash.State("crate-structure-table", "data")]
    )
    def update_crate_songs(clickData, selected_rows, table_data):
        ctx = dash.callback_context
        if not ctx.triggered:
            return []

        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        clicked_path = None

        if trigger_id == "crate-structure-chart" and clickData:
            point = clickData['points'][0]
            clicked_path = point.get('id')
        elif trigger_id == "crate-structure-table" and selected_rows and table_data:
            selected_row_index = selected_rows[0]
            if selected_row_index < len(table_data):
                clicked_path = table_data[selected_row_index].get("Crate Path")
                # Table paths use ' / ' as separator, sunburst uses '/'
                if clicked_path:
                    clicked_path = clicked_path.replace(" / ", "/")

        if not clicked_path:
             return []
        
        clicked_parts = clicked_path.split("/")
        crates = get_crates()
        target_crate_ids = []
        
        # Find all crates that are at or below the clicked path
        for crate in crates:
            parts = [p.strip() for p in crate["name"].split("-") if p.strip()]
            if len(parts) >= len(clicked_parts) and parts[:len(clicked_parts)] == clicked_parts:
                target_crate_ids.append(crate['id'])
        
        if target_crate_ids:
             all_songs = []
             for crate_id in target_crate_ids:
                 songs = get_songs_for_crate(crate_id)
                 if songs:
                     all_songs.extend(songs)
                     
             if not all_songs:
                 return []
                 
             df = pd.DataFrame(all_songs)
             # Drop duplicates in case a song is in multiple subcrates
             df = df.drop_duplicates(subset=['artist', 'title'])
             
             df["bpm"] = pd.to_numeric(df["bpm"], errors="coerce")
            
             # Handle any missing BPMs so dash_table numeric formatting doesn't crash 
             df["bpm"] = df["bpm"].fillna(0)
             
             df["duration"] = pd.to_numeric(df["duration"], errors="coerce")
             df["duration"] = df["duration"].apply(lambda x: format_duration(x) if pd.notna(x) else "N/A")
             
             df = df.sort_values(["artist", "title"])
             return df.to_dict("records")
        return []
