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
        html.Br(),
                dbc.Row([
                    dbc.Col(html.H5("Filter set by date"), width=12)
                 ]),
                dcc.DatePickerRange(
                    id="date-range-picker",
                    start_date=default_start,
                    end_date=default_end,
                    start_date_placeholder_text="Start Date",
                    end_date_placeholder_text="End Date"
                ),
                dbc.Row([
                    # ── Style toggles ──
                    dbc.Label("\n Filter by set style:"),
                    dbc.Checklist(
                        id="style-filter",
                        options=[
                            {"label": "Blues", "value": "blues"},
                            {"label": "Lindy", "value": "lindy"},
                        ],
                        value=["blues", "lindy"],
                        inline=True,
                        switch=True,
                    ),
                ]),
                html.Br(),
        dbc.Row([
            dbc.Col([
                html.H5("Choose set to analyze"),
                dcc.Dropdown(
                    id="sets-dropdown",
                    options=options,
                    value=default_value,  # Preselect all playlists
                    multi=True,
                    placeholder="Choose party sets"
                ),
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
            dbc.Col(html.H5("Most played songs"), width=12)
        ]),
        dbc.Row([
            dbc.Col(
                dash_table.DataTable(
                    id="played-songs-table",
                    columns=[
                        {"name": "Times\n Played", "id": "Times Played", "type": "numeric"},
                        {"name": "Song", "id": "Song"},
                        {"name": "Artists", "id": "Artists"},
                        {"name": "Dates\n Played", "id": "Dates"},
                        {"name": "Rating", "id": "Rating"}
                    ],
                    data=[],
                    sort_action="native",
                    page_size=30,
                    style_table={'overflowX': 'auto'},
                    style_cell={'textAlign': 'left', "fontSize": "14px"},
                    style_cell_conditional=[
                        {'if': {'column_id': 'Times Played'}, 'width': '20px', 'maxWidth': '40px','textAlign': 'center'},
                        {'if': {'column_id': 'Song'}, 'width': '180px', 'maxWidth': '230px', 'overflow': 'hidden', 'textOverflow': 'ellipsis'},
                        {'if': {'column_id': 'Artists'}, 'width': '100px', 'maxWidth': '120px', 'overflow': 'hidden', 'textOverflow': 'ellipsis'},
                        {'if': {'column_id': 'Dates'}, 'width': '120px', 'maxWidth': '150px'},
                        {'if': {'column_id': 'Rating'}, 'width': '30px', 'maxWidth': '40px','textAlign': 'center'}
                    ]
                ),
                width=12
            )
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col(html.H5("Most played Artists"), width=12)
        ]),
        dbc.Row([
            dbc.Col(
                dash_table.DataTable(
                    id="artist-played-table",
                    columns=[
                        {"name": "Artists", "id": "standardized_artist"},
                        {"name": "Times Played", "id": "count", "type": "numeric"},
                        {"name": "Songs Count", "id": "played_songs_per_artist", "type": "numeric"}
                    ],
                    data=[],
                    sort_action="native",
                    page_size=15,
                    style_table={'overflowX': 'auto'},
                    style_cell={'textAlign': 'left', "fontSize": "14px"},
                    style_cell_conditional=[
                        {'if': {'column_id': 'standardized_artist'}, 'width': '180px', 'maxWidth': '230px', 'overflow': 'hidden', 'textOverflow': 'ellipsis'},
                        {'if': {'column_id': 'count'}, 'width': '50px', 'maxWidth': '50px','textAlign': 'center'},
                        {'if': {'column_id': 'played_songs_per_artist'}, 'width': '50px', 'maxWidth': '50px','textAlign': 'center'}
                ],
                style_as_list_view=True,
                )
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
                    columns=[{"name": "Artists", "id": "Artists"}],
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
                {"name": "BPM", "id": "bpm", "type":"numeric"},
                {"name": "Duration", "id": "duration", "type":"numeric"}
            ],
            data=[],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', "fontSize": "14px"},
            style_cell_conditional=[
                {'if': {'column_id': 'artist'}, 'width': '60px', 'maxWidth': '90px','textAlign': 'left'},
                {'if': {'column_id': 'title'}, 'width': '130px', 'maxWidth': '150px', 'overflow': 'hidden', 'textOverflow': 'ellipsis'},
                {'if': {'column_id': 'album'}, 'width': '100px', 'maxWidth': '120px', 'overflow': 'hidden', 'textOverflow': 'ellipsis'},
                {'if': {'column_id': 'bpm'}, 'width': '20px', 'maxWidth': '40px'},
                {'if': {'column_id': 'duration'}, 'width': '30px', 'maxWidth': '40px','textAlign': 'center'}
            ],
        style_header={
        'backgroundColor': 'rgb(210, 210, 210)',
        'color': 'black',
        'fontWeight': 'bold'
        }
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
            data=[],
            page_size=30,
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', "fontSize": "14px"}
        )
    ])

def songs_layout():
    return html.Div([
        html.H3("Songs research"),
        # Add crate-related components here.
        html.Div("A tab where I ran research my songs.")
    ])
