import os
import sys

def get_base_path():
    """Returns the base path for the application.
    If bundled, this is the directory where the executable is located.
    If running from source, this is the project root.
    """
    if getattr(sys, 'frozen', False):
        # Running in a bundle
        # For --onedir, this is the folder containing the executable
        # For --onefile, this is the temp folder _MEIPASS
        # But for persistent data (like databases), we want the folder containing the executable
        return os.path.dirname(sys.executable)
    else:
        # Running from source
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller.
    Used for READ-ONLY assets (images, css) that are bundled INSIDE the executable.
    """
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def get_data_path(relative_path):
    """Get absolute path to data file, works for dev and for PyInstaller.
    Used for WRITABLE data (sqlite, config.json) that should be PERSISTENT.
    """
    return os.path.join(get_base_path(), relative_path)
