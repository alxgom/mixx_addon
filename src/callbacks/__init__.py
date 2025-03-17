from .aggregate import register_aggregate_callbacks, shared_data, party_set_options, playlist_id_to_date, default_start, default_end
from .crates import register_crates_callbacks
from .individual import register_individual_callbacks
from .library import register_library_callbacks

def register_callbacks(app):
    register_aggregate_callbacks(app)
    register_crates_callbacks(app)
    register_individual_callbacks(app)
    register_library_callbacks(app)
