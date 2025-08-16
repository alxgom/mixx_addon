from .aggregate import register_aggregate_callbacks
from .crates import register_crates_callbacks
from .individual import register_individual_callbacks
from .library import register_library_callbacks
from .tabs_content import register_tabs_callbacks
from .songs import register_songs_callbacks
from .plotly_template import register_swing_theme
from .shared import get_shared_data, clean_and_split_artists
#from .spot import export_mixxx_to_spotif

# Compute shared data once for initial defaults.
shared_data = get_shared_data()
party_set_options = shared_data["party_set_options"]
default_start = shared_data["default_start"]
default_end = shared_data["default_end"]

def register_callbacks(app):
    register_tabs_callbacks(app)       # This updates the "tab-content" container.
    register_aggregate_callbacks(app)
    register_crates_callbacks(app)
    register_individual_callbacks(app)
    register_library_callbacks(app)
    register_songs_callbacks(app)

