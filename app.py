from dash import Dash
import dash_bootstrap_components as dbc
from src.layouts.layout import get_layout
from src.callbacks import register_callbacks, party_set_options, default_start, default_end

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server #expose to flask
app.layout = get_layout(party_set_options, default_start, default_end)
register_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)
