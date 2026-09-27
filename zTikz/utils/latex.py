"""Finding pdflatex, and OS-specific hints for the settings dialog.

GUI programs don't always inherit the shell's PATH (a Finder-launched macOS app only
sees a minimal one), so besides PATH we also look in the usual TeX install folders.
"""
import glob
import os
import shutil
import sys


def _is_executable(path):
    return os.path.isfile(path) and os.access(path, os.X_OK)


def known_location_patterns(platform=None, environ=None):
    """Glob patterns where TeX distributions usually install pdflatex."""
    platform = platform or sys.platform
    env = os.environ if environ is None else environ
    home = os.path.expanduser("~")

    if platform == "win32":
        patterns = []
        for var, parts in (("LOCALAPPDATA", ("Programs", "MiKTeX", "miktex", "bin", "x64", "pdflatex.exe")),
                           ("PROGRAMFILES", ("MiKTeX", "miktex", "bin", "x64", "pdflatex.exe")),
                           ("USERPROFILE", ("texlive", "*", "bin", "*", "pdflatex.exe"))):
            if env.get(var):
                patterns.append(os.path.join(env[var], *parts))
        patterns.append("C:\\texlive\\*\\bin\\*\\pdflatex.exe")
        return patterns

    if platform == "darwin":
        return ["/Library/TeX/texbin/pdflatex",
                "/usr/local/texlive/*/bin/*/pdflatex",
                "/opt/homebrew/bin/pdflatex",
                "/usr/local/bin/pdflatex",
                os.path.join(home, "Library", "TeX", "texbin", "pdflatex")]

    return ["/usr/bin/pdflatex",
            "/usr/local/bin/pdflatex",
            "/usr/local/texlive/*/bin/*/pdflatex",
            "/opt/texlive/*/bin/*/pdflatex",
            os.path.join(home, "texlive", "*", "bin", "*", "pdflatex")]


def find_pdflatex(configured=None, platform=None, environ=None):
    """Return the pdflatex executable to use, or None if there isn't a usable one.

    A path configured in Settings wins and is never silently replaced: if it is wrong
    the caller gets None and can say so. Without one, PATH is searched first and then
    the usual install folders (newest TeX Live year first).
    """
    if configured and configured.strip():
        path = os.path.expanduser(configured.strip().strip('"'))
        if os.path.isdir(path):                      # a folder was given: look inside it
            for name in ("pdflatex", "pdflatex.exe"):
                if _is_executable(os.path.join(path, name)):
                    return os.path.join(path, name)
            return None
        return path if _is_executable(path) else None

    found = shutil.which("pdflatex")
    if found:
        return found
    for pattern in known_location_patterns(platform, environ):
        for match in sorted(glob.glob(pattern), reverse=True):
            if _is_executable(match):
                return match
    return None


def subprocess_env(pdflatex):
    """Environment for running pdflatex: its own folder first on PATH, so the helper
    programs it starts are found even when the app itself was launched with a short PATH."""
    env = os.environ.copy()
    folder = os.path.dirname(os.path.abspath(pdflatex))
    env["PATH"] = folder + os.pathsep + env.get("PATH", "")
    return env


def executable_file_filter(platform=None):
    """File-dialog filter for picking a program: only Windows executables carry an extension."""
    if (platform or sys.platform) == "win32":
        return "Executables (*.exe);;All Files (*)"
    return "All Files (*)"


def pdflatex_placeholder(platform=None):
    platform = platform or sys.platform
    if platform == "win32":
        return "e.g. C:\\texlive\\2025\\bin\\windows\\pdflatex.exe"
    if platform == "darwin":
        return "e.g. /Library/TeX/texbin/pdflatex"
    return "e.g. /usr/bin/pdflatex"


def pdf_viewer_placeholder(platform=None):
    platform = platform or sys.platform
    if platform == "win32":
        return "e.g. C:\\Program Files\\SumatraPDF\\SumatraPDF.exe"
    if platform == "darwin":
        return "e.g. /Applications/Skim.app"
    return "e.g. /usr/bin/okular"
