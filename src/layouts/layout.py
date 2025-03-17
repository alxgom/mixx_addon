import dash_bootstrap_components as dbc
from dash import dcc, html

def get_layout(party_set_options, default_start, default_end):
    layout = dbc.Container([
        html.H2("Mixxx Metadata Dashboard"),
        dbc.Tabs(
            [
                dbc.Tab(label="Aggregate Playlists", tab_id="aggregate"),
                dbc.Tab(label="Crate Analysis", tab_id="crates"),
                dbc.Tab(label="Individual Playlists", tab_id="individual"),
                dbc.Tab(label="Library", tab_id="library")
            ],
            id="tabs",
            active_tab="aggregate"
        ),
        html.Div(id="tab-content")
    ], fluid=True)
    return layout
