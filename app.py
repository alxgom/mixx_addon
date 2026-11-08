# This is a dashboard to analyze the dj sets i played at swing and blues dance socials, using the MIXXX open source app.
# Agregate tab gives an overview analysis of the sets played.
# Individual playlist tab shows the analysis of the sets played at each social.
# Library tab shows the analysis of all the song I have on my library.
# 



import os
import sys
from dash import Dash
import dash_bootstrap_components as dbc
from src.layouts.layout import get_layout
from src.callbacks import register_callbacks, party_set_options, default_start, default_end
from src.db.notes_db import init_db, upsert_note
from flask import request

from src.paths import get_resource_path

init_db()  # ensures database and table exist
app = Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP], 
    suppress_callback_exceptions=True,
    assets_folder=get_resource_path('assets')
)
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
    import webbrowser
    from waitress import serve
    
    port = 8050
    url = f"http://127.0.0.1:{port}"
    
    if getattr(sys, 'frozen', False):
        # Production build (executable)
        import socket
        import threading

        # Single instance: if the server is already running, just open the browser.
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            already_running = s.connect_ex(('127.0.0.1', port)) == 0
        if already_running:
            webbrowser.open(url)
            sys.exit(0)

        import pystray
        from PIL import Image, ImageDraw

        threading.Thread(
            target=lambda: serve(app.server, host='127.0.0.1', port=port),
            daemon=True,
        ).start()
        threading.Timer(1, lambda: webbrowser.open(url)).start()

        # Simple generated tray icon (vinyl-like disc)
        img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse((2, 2, 62, 62), fill=(30, 30, 30, 255))
        draw.ellipse((22, 22, 42, 42), fill=(230, 120, 40, 255))
        draw.ellipse((29, 29, 35, 35), fill=(30, 30, 30, 255))

        def on_quit(icon, item):
            icon.stop()
            os._exit(0)  # terminates the waitress thread

        icon = pystray.Icon(
            'mixxx_dashboard',
            img,
            'Mixxx DJ Dashboard',
            menu=pystray.Menu(
                pystray.MenuItem('Open dashboard', lambda icon, item: webbrowser.open(url), default=True),
                pystray.MenuItem('Quit', on_quit),
            ),
        )
        icon.run()
    else:
        # Development mode (running app.py directly)
        # Timer helps ensure the server is up before the browser opens
        from threading import Timer
        Timer(1, lambda: webbrowser.open(url)).start()
        app.run(debug=True, port=port)
