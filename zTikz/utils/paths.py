"""Where zTikz keeps its files.

Nothing is written inside the installed package: after ``pip install`` that folder can
be read-only (system-wide Linux installs, a signed macOS app bundle, Program Files).

* Read-only resources (icons, snippets, the default preamble) live in the package.
* The user's editable preamble lives in a per-user data folder.
* Compilation output lives in a temporary folder created per running session.

Set the ``ZTIKZ_DATA_DIR`` environment variable to use a different data folder
(portable installs, tests).
"""
import os
import shutil
import tempfile

from PyQt6.QtCore import QStandardPaths

APP_DIR_NAME = "zTikz"
DATA_DIR_ENV = "ZTIKZ_DATA_DIR"


def resources_dir():
    """The package's read-only resources folder."""
    return os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resources"))


def default_preamble_path():
    """The pristine preamble shipped with the app (never modified)."""
    return os.path.join(resources_dir(), "preamble.default.tex")


def legacy_preamble_path():
    """Older versions kept the editable preamble inside the package folder."""
    return os.path.join(resources_dir(), "preamble.tex")


def user_data_dir():
    """Per-user data folder: %LOCALAPPDATA%\\zTikz, ~/.local/share/zTikz or
    ~/Library/Application Support/zTikz. Not created here."""
    override = os.environ.get(DATA_DIR_ENV)
    if override:
        return os.path.abspath(os.path.expanduser(override))
    base = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.GenericDataLocation)
    if not base:
        base = os.path.join(os.path.expanduser("~"), ".local", "share")
    return os.path.join(os.path.normpath(base), APP_DIR_NAME)


def user_preamble_path():
    return os.path.join(user_data_dir(), "preamble.tex")


def _read_bytes(path):
    with open(path, "rb") as f:
        return f.read()


def ensure_user_preamble(legacy_path=None):
    """Return the path of the user's preamble, creating it on first use.

    The first copy comes from the shipped default. If an older version left an edited
    preamble inside the package folder, that one is kept instead so edits aren't lost.
    Raises OSError if the data folder can't be written.
    """
    path = user_preamble_path()
    if os.path.exists(path):
        return path

    source = default_preamble_path()
    legacy = legacy_preamble_path() if legacy_path is None else legacy_path
    if os.path.isfile(legacy) and _read_bytes(legacy) != _read_bytes(source):
        source = legacy

    os.makedirs(os.path.dirname(path), exist_ok=True)
    shutil.copyfile(source, path)
    return path


def new_session_temp_dir():
    """A fresh private folder for one running session's compilation files."""
    return tempfile.mkdtemp(prefix="ztikz-")
