from dash import Dash
import dash_bootstrap_components as dbc
from src.layouts.layout import get_layout
from src.callbacks import register_callbacks, party_set_options, default_start, default_end
from src.db.notes_db import init_db, upsert_note

init_db()  # ensures database and table exist
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server #expose to flask
app.layout = get_layout(party_set_options, default_start, default_end)
register_callbacks(app)

if __name__ == '__main__':
    app.run(debug=True)
