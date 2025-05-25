from dash import html, dcc, dash_table,Input, Output
import dash_bootstrap_components as dbc
from src.callbacks.shared import get_shared_data
from dash.dash_table.Format import Format, Scheme, Trim
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
                html.Img(src="/assets/test_img.jpg", className="banner-img"),
                dbc.Col(html.H1(children=[
                    html.Span("Analyze ", className="title-orange"),
                    html.Span("party ", className="title-pink"),
                    html.Span("sets", className="title-green")
                    ]                   
                    ,className="dashboard-title"
                    ), md=12, sm=12)
                ], style={"marginBottom": "40px","marginTop": "10px"}, className="banner-container"),
                dbc.Row([
                    dbc.Col(html.H3("Filter set by date"), md=3, sm=3),
                dbc.Col(dcc.DatePickerRange(
                    id="date-range-picker",
                    start_date=default_start,
                    end_date=default_end,
                    start_date_placeholder_text="Start Date",
                    end_date_placeholder_text="End Date"
                ),md=4, sm=4),
                ]),
                dbc.Row([
                    # ── Style toggles ──
                    dbc.Col(html.H4("\n Filter by set style"), md=3, sm=3),
                    dbc.Col(dbc.Checklist(
                        id="style-filter",
                        options=[
                            {"label": "Blues", "value": "blues"},
                            {"label": "Lindy", "value": "lindy"},
                        ],
                        value=["blues", "lindy"],
                        inline=True,
                        switch=True,
                    ), md=4, sm=4
                    ),
                ]),
                html.Br(),
        dbc.Row([
            dbc.Col([
                html.H4("Filter by sets"),
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
            dbc.Col(dbc.Card(html.H5(id="total-songs", children="Total Songs: 0",className="text-center"), body=True), width=6, className="mb-2"),
            dbc.Col(dbc.Card(html.H5(id="avg-duration", children="Avg Duration: 0",className="text-center"), body=True), width=6)
        ], style={"marginBottom": "10px"}),
        dbc.Row([
            dbc.Col(dbc.Card(html.H5(id="unique-songs", children="Unique Songs: 0",className="text-center"), body=True), width=6, className="mb-2"),
            dbc.Col(dbc.Card(html.H5(id="unique-artists", children="Unique Artists: 0",className="text-center"), body=True), width=6)
        ], style={"marginBottom": "20px"}),
        dbc.Row([
            dbc.Col([
                dbc.Row(dbc.Card(html.H6(id="avg-bpm", children="Avg BPM: 0"), body=True), className="mb-2"),
                dbc.Row(dbc.Card(dcc.Markdown(id="fastest-song"), body=True), className="mb-2"),# Initial empty dcc.Markdown
            dbc.Row(dbc.Card(dcc.Markdown(id="slowest-song"), body=True))
            ], md=4,sm=12),
            dbc.Col([
                dbc.Row(dcc.Graph(id="bpm-histogram"))
            ], md=8,sm=12)
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id="bpm-boxplot"),sm=12)
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col(html.H4("Most played songs",className="text-center"), width=12),
            dbc.Col(dbc.Card(html.H4(id="top-played-song", children="Top Played Song: -"), body=True), width=12)
        ], style={"marginTop": "20px"}),
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
                    sort_by=[{'column_id': 'Times Played', 'direction': 'desc'}],
                    sort_action="native",
                    filter_options={"case": "insensitive"},  # Set case-insensitive filtering
                    page_size=30,
                    virtualization=True,
                    fixed_rows={'headers': True},
                    style_cell_conditional=[
                        {'if': {'column_id': 'Times Played'}, 'width': '20px', 'maxWidth': '40px','textAlign': 'center'},
                        {'if': {'column_id': 'Song'}, 'width': '180px', 'maxWidth': '230px', 'overflow': 'hidden', 'textOverflow': 'ellipsis'},
                        {'if': {'column_id': 'Artists'}, 'width': '100px', 'maxWidth': '120px', 'overflow': 'hidden', 'textOverflow': 'ellipsis'},
                        {'if': {'column_id': 'Dates'}, 'width': '120px', 'maxWidth': '150px'},
                        {'if': {'column_id': 'Rating'}, 'width': '30px', 'maxWidth': '40px','textAlign': 'center'}
                    ],
                style_table={
                    'height': 800,
                    'overflowX': 'auto',    
                    "border": "1px solid #CBA135",
                    "boxShadow": "0 2px 6px rgba(0,0,0,0.1)"
                },
                style_header={
                    "backgroundColor": "#FFFDF8",
                    "fontWeight": "bold",
                    "fontFamily": "Raleway",
                    "color": "#2C3E50"
                },
                style_cell={
                    'textAlign': 'left',
                    "fontSize": "14px",
                    "fontFamily": "Quicksand",
                    "backgroundColor": "#F6F1EB",
                    "color": "#3A3A3A",
                    "padding": "8px",
                    "border": "none"
                }
                ),
                width=12
            )
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col(html.H4("Most played Artists",className="text-center"), width=12),
            dbc.Col(dbc.Card(html.H4(id="top-played-artist", children="Top Played Artist: -"), body=True), width=12)
        ], style={"marginTop": "20px"}),
        dbc.Row([          
            dbc.Col(dcc.Graph(id="artist-bar-chart"), md=6,sm=12),
            dbc.Col(
                dash_table.DataTable(
                    id="artist-played-table",
                    columns=[
                        {"name": "Artists", "id": "standardized_artist"},
                        {"name": "Times Played", "id": "count", "type": "numeric"},
                        {"name": "Songs Count", "id": "played_songs_per_artist", "type": "numeric"}
                    ],
                    data=[],
                    sort_by=[{'column_id': 'count', 'direction': 'desc'}],
                    sort_action="native",
                    filter_action="native",
                    page_size=40,
                    virtualization=True,
                    fixed_rows={'headers': True},
                    style_cell_conditional=[
                        {'if': {'column_id': 'standardized_artist'}, 'width': '140px', 'maxWidth': '160px', 'overflow': 'hidden', 'textOverflow': 'ellipsis'},
                        {'if': {'column_id': 'count'}, 'width': '70px', 'maxWidth': '70px','textAlign': 'center'},
                        {'if': {'column_id': 'played_songs_per_artist'}, 'width': '70px', 'maxWidth': '70px','textAlign': 'center'}
                ],
                style_as_list_view=True,
                style_table={
                    'height': 600,
                    'overflowX': 'auto',    
                    "border": "1px solid #CBA135",
                    "boxShadow": "0 2px 6px rgba(0,0,0,0.1)"
                },
                style_header={
                    "backgroundColor": "#FFFDF8",
                    "fontWeight": "bold",
                    "fontFamily": "Raleway",
                    "color": "#2C3E50"
                },
                style_cell={
                    'textAlign': 'left',
                    "fontSize": "14px",
                    "fontFamily": "Quicksand",
                    "backgroundColor": "#F6F1EB",
                    "color": "#3A3A3A",
                    "padding": "8px",
                    "border": "none"
                }
                ),
            md=6,sm=12)
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
                {"name": "Title", "id": "title"},
                {"name": "Artist", "id": "artist"},
                {"name": "Album", "id": "album"},
                {"name": "BPM", "id": "bpm", "type":"numeric", "format":Format(precision=2, scheme=Scheme.decimal_integer)},
                {"name": "Duration", "id": "duration", "type":"numeric"}
            ],
            data=[],
            style_cell_conditional=[
                {'if': {'column_id': 'artist'}, 'width': '60px', 'maxWidth': '90px','textAlign': 'left'},
                {'if': {'column_id': 'title'}, 'width': '130px', 'maxWidth': '150px', 'overflow': 'hidden', 'textOverflow': 'ellipsis'},
                {'if': {'column_id': 'album'}, 'width': '100px', 'maxWidth': '120px', 'overflow': 'hidden', 'textOverflow': 'ellipsis'},
                {'if': {'column_id': 'bpm'}, 'width': '20px', 'maxWidth': '40px','textAlign': 'center'},
                {'if': {'column_id': 'duration'}, 'width': '30px', 'maxWidth': '40px','textAlign': 'center'}
            ],
            style_table={
            'height': 600,
            'overflowX': 'auto',    
            "border": "1px solid #CBA135",
            "boxShadow": "0 2px 6px rgba(0,0,0,0.1)",
            "margin-top": "1em",
            "margin-bottom": "10px"
        },
        style_header={
            "backgroundColor": "#FFFDF8",
            "fontWeight": "bold",
            "fontFamily": "Raleway",
            "color": "#2C3E50"
        },
        style_cell={
            'textAlign': 'left',
            "fontSize": "14px",
            "fontFamily": "Quicksand",
            "backgroundColor": "#F6F1EB",
            "color": "#3A3A3A",
            "padding": "8px",
            "border": "none"
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
                {"name": "Title", "id": "title"},
                {"name": "Artist", "id": "artist"},
                {"name": "Album", "id": "album"},
                {"name": "BPM", "id": "bpm", "type":"numeric", "format":Format(precision=2, scheme=Scheme.decimal_integer)},
                {"name": "Rating", "id": "rating", "type": "numeric"}
            ],
            sort_action="native",
            filter_action="native",
            filter_options={"case": "insensitive"},  # Set case-insensitive filtering
            data=[],
            virtualization=True,
            fixed_rows={'headers': True},
            page_size=200,
            style_cell_conditional=[
                {'if': {'column_id': 'rating'}, 'width': '10px', 'maxWidth': '30px','textAlign': 'center'},
                {'if': {'column_id': 'bpm'}, 'width': '10px', 'maxWidth': '30px','textAlign': 'center'},
                {'if': {'column_id': 'artist'}, 'width': '60px', 'maxWidth': '90px','textAlign': 'left'},
                {'if': {'column_id': 'title'}, 'width': '130px', 'maxWidth': '150px', 'overflow': 'hidden', 'textOverflow': 'ellipsis'},
                {'if': {'column_id': 'album'}, 'width': '80px', 'maxWidth': '100px', 'overflow': 'hidden', 'textOverflow': 'ellipsis'}
            ],
            style_table={
            'height': 600,
            "margin-top": "1em",
            'overflowX': 'auto',    
            "border": "1px solid #CBA135",
            "boxShadow": "0 2px 6px rgba(0,0,0,0.1)"
        },
        style_header={
            "backgroundColor": "#FFFDF8",
            "fontWeight": "bold",
            "fontFamily": "Raleway",
            "color": "#2C3E50"
        },
        style_cell={
            'textAlign': 'left',
            "fontSize": "14px",
            "fontFamily": "Quicksand",
            "backgroundColor": "#F6F1EB",
            "color": "#3A3A3A",
            "padding": "8px",
            "border": "none"
        }
       )  
    ])

def songs_layout():
    return html.Div([
        html.H3("Songs research"),
        html.H2("Song Search Tool"),
        # Add crate-related components here.
        html.Div("A tab where I ran research my songs."),
        dcc.Input(
        id='search-input',
        type='text',
        placeholder='Search by song or artist...',
        debounce=True,  # triggers update only when user stops typing
        style={'width': '100%', 'padding': '10px', 'fontSize': '16px'}
    ),
    dash_table.DataTable(
        id='results-table',
        columns=[
            {'name': col, 'id': col} for col in df.columns
        ],
        data=[],
        style_table={'overflowX': 'auto'},
        page_size=10,
    )
    ])
