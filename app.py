# This is a dashboard to analyze the dj sets i played at swing and blues dance socials, using the MIXXX open source app.
# Agregate tab gives an overview analysis of the sets played.
# Individual playlist tab shows the analysis of the sets played at each social.
# Library tab shows the analysis of all the song I have on my library.
# 



from dash import Dash
import dash_bootstrap_components as dbc
from src.layouts.layout import get_layout
from src.callbacks import register_callbacks, party_set_options, default_start, default_end
from src.db.notes_db import init_db, upsert_note
from flask import request

init_db()  # ensures database and table exist
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server #expose to flask

@server.before_request
def check_spotify_callback():
    # If Spotify redirects back here with a code, intercept it!
    if request.path == '/' and 'code' in request.args:
        code = request.args.get('code')
        try:
            from src.callbacks.individual import get_auth_manager
            auth_manager = get_auth_manager()
            auth_manager.get_access_token(code)
            return "✅ Spotify authorization successful! You can safely close this tab and click 'Export to Spotify' again in your main dashboard."
        except Exception as e:
            return f"❌ Spotify authorization failed: {e}"

app.layout = get_layout(party_set_options, default_start, default_end)
register_callbacks(app)

if __name__ == '__main__':
    app.run(debug=True)
