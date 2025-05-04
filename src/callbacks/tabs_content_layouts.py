from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from src.callbacks.shared import get_shared_data

def aggregate_layout():
    shared = get_shared_data()
    default_start = shared["default_start"]
    default_end = shared["default_end"]
    options = shared["party_set_options"]
    # Preselect all playlists by default.
    default_value = [opt["value"] for opt in options]
    
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H5("Filters"),
                dcc.Dropdown(
                    id="sets-dropdown",
                    options=options,
                    value=default_value,  # Preselect all playlists
                    multi=True,
                    placeholder="Choose party sets"
                ),
                html.Br(),
                dcc.DatePickerRange(
                    id="date-range-picker",
                    start_date=default_start,
                    end_date=default_end,
                    start_date_placeholder_text="Start Date",
                    end_date_placeholder_text="End Date"
                )
            ], width=12)
        ], style={"marginBottom": "20px"}),
        dbc.Row([
            dbc.Col(dbc.Card(html.H6(id="total-songs", children="Total Songs: 0"), body=True), width=4),
            dbc.Col(dbc.Card(html.H6(id="unique-songs", children="Unique Songs: 0"), body=True), width=4),
            dbc.Col(dbc.Card(html.H6(id="unique-artists", children="Unique Artists: 0"), body=True), width=4)
        ], style={"marginBottom": "10px"}),
        dbc.Row([
            dbc.Col(dbc.Card(html.H6(id="avg-bpm", children="Avg BPM: 0"), body=True), width=4),
            dbc.Col(dbc.Card(html.H6(id="top-played-artist", children="Top Played Artist: -"), body=True), width=4),
            dbc.Col(dbc.Card(html.H6(id="top-played-song", children="Top Played Song: -"), body=True), width=4)
        ], style={"marginBottom": "10px"}),
        dbc.Row([
            dbc.Col(dbc.Card(html.H6(id="avg-duration", children="Avg Duration: 0"), body=True), width=4),
            dbc.Col(dbc.Card(html.H6(id="fastest-song", children="Fastest Song: -"), body=True), width=4),
            dbc.Col(dbc.Card(html.H6(id="slowest-song", children="Slowest Song: -"), body=True), width=4)
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id="bpm-histogram"), width=6),
            dbc.Col(dcc.Graph(id="artist-bar-chart"), width=6)
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id="bpm-boxplot"), width=12)
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col(
                dash_table.DataTable(
                    id="played-songs-table",
                    columns=[
                        {"name": "Times Played", "id": "Times Played", "type": "numeric"},
                        {"name": "Song", "id": "Song"},
                        {"name": "Artist", "id": "Artist"},
                        {"name": "Dates", "id": "Dates"},
                        {"name": "Rating", "id": "Rating"}
                    ],
                    data=[],
                    sort_action="native",
                    page_size=40,
                    style_table={'overflowX': 'auto'},
                    style_cell={'textAlign': 'left', "fontSize": "14px"},
                    style_cell_conditional=[{'if': {'column_id': 'Artist'}, 'width': '80px'}]
                ),
                width=12
            )
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col(
                dash_table.DataTable(
                    id="artist-played-table",
                    columns=[
                        {"name": "Artist", "id": "Artist"},
                        {"name": "Times Played", "id": "Times Played", "type": "numeric"},
                        {"name": "Songs Count", "id": "Songs Count", "type": "numeric"}
                    ],
                    data=[],
                    sort_action="native",
                    page_size=40,
                    style_table={'overflowX': 'auto'},
                    style_cell={'textAlign': 'left', "fontSize": "14px"}
                ),
                width=12
            )
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col(html.H5("Unplayed Artists"), width=12)
        ]),
        dbc.Row([
            dbc.Col(
                dash_table.DataTable(
                    id="unplayed-artists-table",
                    columns=[{"name": "Artist", "id": "Artist"}],
                    data=[],
                    sort_action="native",
                    page_size=40,
                    style_table={'overflowX': 'auto'},
                    style_cell={'textAlign': 'left', "fontSize": "14px"}
                ),
                width=12
            )
        ])
    ])

def crates_layout():
    return html.Div([
        html.H3("Crate Analysis"),
        # Add crate-related components here.
        html.Div("Crate Analysis content goes here")
    ])

def individual_layout():
    # For the individual layout, you can also get fresh shared data if needed.
    shared = get_shared_data()
    options = shared["party_set_options"]
    return html.Div([
        html.H3("Individual Playlist Analysis"),
        dcc.Dropdown(
            id="individual-playlist-dropdown",
            options=options,
            placeholder="Choose a playlist"
        ),
        dash_table.DataTable(
            id="individual-playlist-table",
            columns=[
                {"name": "Artist", "id": "artist"},
                {"name": "Title", "id": "title"},
                {"name": "Album", "id": "album"},
                {"name": "BPM", "id": "bpm"},
                {"name": "Duration", "id": "duration"}
            ],
            data=[]
        ),
        dcc.Graph(id="individual-playlist-cumulative-plot"),

        dbc.Button("Export to Spotify", id="export-spotify-btn", color="success", className="mt-2"),
        html.Div(id="export-spotify-link", className="mt-2")
    ])

def library_layout():
    return html.Div([
        html.H3("Library Data"),
        dbc.Row([
            dbc.Col(dbc.Card(html.H6(id="library-total-songs", children="Total Songs: 0"), body=True), width=3)
        ]),
        dcc.Graph(id="library-rating-distribution"),
        dash_table.DataTable(
            id="library-table",
            columns=[
                {"name": "ID", "id": "id"},
                {"name": "Artist", "id": "artist"},
                {"name": "Title", "id": "title"},
                {"name": "Album", "id": "album"},
                {"name": "Rating", "id": "rating"}
            ],
            data=[]
        )
    ])
