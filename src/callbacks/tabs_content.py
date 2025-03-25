import dash
from dash import html
from .tabs_content_layouts import aggregate_layout, crates_layout, individual_layout, library_layout

def register_tabs_callbacks(app):
    @app.callback(
        dash.Output("tab-content", "children"),
        dash.Input("tabs", "active_tab")
    )
    def render_tab_content(active_tab):
        print("Rendering content for tab:", active_tab)
        if active_tab == "aggregate":
            return aggregate_layout()
        elif active_tab == "crates":
            return crates_layout()
        elif active_tab == "individual":
            return individual_layout()
        elif active_tab == "library":
            return library_layout()
        return html.Div("Tab not found")
