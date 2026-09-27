import glob
import os
import shutil
import sys
import math
import hashlib
import re
import time
from types import SimpleNamespace

from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtCore import Qt, QEventLoop, QProcess, QProcessEnvironment, QTimer
from PyQt6.QtGui import QPixmap, QTextCursor
import fitz

# Note: tikz_parser is defined in tikz_parser.py, so we import it here.
from zTikz.parser.parser import tikz_parser
from zTikz.utils import paths as app_paths
from zTikz.utils.latex import find_pdflatex, subprocess_env
from zTikz.utils.translations import tr


def read_text_file(path):
    """Read a text file as UTF-8 (with or without BOM).

    Falls back to Windows-1252 for legacy files that aren't valid UTF-8, so opening
    such a file never crashes; saving always writes UTF-8.
    """
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            return f.read()
    except UnicodeDecodeError:
        with open(path, "r", encoding="cp1252", errors="replace") as f:
            return f.read()


def refresh_overlay_layers(self):
    """Match overlay behavior: toggle the edit layer, not the preview."""
    has_preview = getattr(self, "original_preview_pixmap", None) is not None

    if has_preview:
        self.preview.show()

        if self.overlay_active:
            self.canvas.show()
            self.canvas.raise_()
            self.canvas.setStyleSheet("background-color: transparent;")
        else:
            self.canvas.hide()
    else:
        self.preview.hide()
        self.canvas.show()
        self.canvas.raise_()
        self.canvas.setStyleSheet("background-color: white;")

def toggle_left_panel(self, index):
    # We define the panel as "open" if the maximum width is not collapsed
    is_open = self.left_tabs.maximumWidth() > 100
    
    if is_open and self.left_tabs.currentIndex() == index:
        # Clicked the currently active tab while open -> Collapse it
        self.stored_sizes = self.main_splitter.sizes()
        tab_bar_width = self.left_tabs.tabBar().sizeHint().width()
        if tab_bar_width < 20: tab_bar_width = 30 # fallback
        self.left_tabs.setMinimumWidth(0)
        self.left_tabs.setMaximumWidth(tab_bar_width)
        self.main_splitter.setSizes([tab_bar_width, self.stored_sizes[1], self.stored_sizes[2]])
    else:
        # It's collapsed OR we clicked a different tab -> Expand it
        self.left_tabs.setMinimumWidth(200)
        self.left_tabs.setMaximumWidth(16777215)
        
        if index == 2: # Preamble (tabs: 0 Files, 1 Snippets, 2 Preamble)
            self.preamble_buttons_widget.show()
            self.preamble_editor.show()
            self.preamble_highlighter.rehighlight()
            
        # Only restore sizes if we are opening it from collapsed state
        if not is_open:
            if hasattr(self, 'stored_sizes'):
                self.main_splitter.setSizes(self.stored_sizes)
            else:
                total = self.main_splitter.width()
                remaining = total - 350
                if remaining > 0:
                    self.main_splitter.setSizes([350, remaining // 3, 2 * remaining // 3])

def save_preamble(self):
    # Save the changes made in the preamble editor to the user's own preamble file
    # (never inside the installed package, which may be read-only).
    try:
        preamble_path = app_paths.user_preamble_path()
        os.makedirs(os.path.dirname(preamble_path), exist_ok=True)
        with open(preamble_path, 'w', encoding='utf-8') as file:
            file.write(self.preamble_editor.toPlainText())
    except OSError as e:
        self.output.appendPlainText("\n" + tr("Could not save the preamble:") + f" {e}")
        return
    # Invalidate caches so next compilation picks up the new preamble
    self._cached_preamble_content = None
    # Changes to the static part are detected by hash; this only allows a retry
    # of a previously failed format build (e.g. after installing a missing package).
    self._fmt_failed_hash = None

def restore_preamble(self):
    """Restore the preamble editor to the default preamble shipped with the app."""
    default_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'preamble.default.tex')
    try:
        default_preamble = read_text_file(default_path)
    except OSError as e:
        self.output.appendPlainText("\n" + tr("Could not read the default preamble:") + f" {e}")
        return
    self.preamble_editor.setPlainText(default_preamble)
    # Auto-save the restored default
    self.save_preamble()

def open_file(self):
    from PyQt6.QtWidgets import QFileDialog

    if not self.confirm_discard_changes():
        return

    file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "TikZ/TeX Files (*.tex *.tikz);;All Files (*)")
    if file_path:
        content = read_text_file(file_path)
        self.editor.setPlainText(content)
        self.editor.document().setModified(False)
        self.current_file_path = file_path
        self.update_window_title()

        # Sync the tree view to this file's folder
        folder = os.path.dirname(file_path)
        self._update_path_ui(folder)
        self._add_to_history(folder)

def save_file(self):
    if hasattr(self, 'current_file_path') and self.current_file_path:
        with open(self.current_file_path, "w", encoding="utf-8") as file:
            file.write(self.editor.toPlainText())
        self.editor.document().setModified(False)
        self.update_window_title()
    else:
        self.save_as_file()

def save_as_file(self):
    from PyQt6.QtWidgets import QFileDialog
    file_path, _ = QFileDialog.getSaveFileName(self, "Save File As", "", "TikZ/TeX Files (*.tex *.tikz);;All Files (*)")
    if file_path:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(self.editor.toPlainText())
        self.editor.document().setModified(False)
        self.current_file_path = file_path
        self.update_window_title()

def confirm_discard_changes(self):
    """Ask what to do with unsaved changes. Returns True if it is safe to continue
    (nothing to save, changes saved, or discarded) and False if the user cancelled
    or the save did not complete."""
    from PyQt6.QtWidgets import QMessageBox

    if not self.editor.document().isModified():
        return True

    reply = QMessageBox.question(
        self, tr('Save Changes?'),
        tr('Do you want to save the current document before continuing?'),
        QMessageBox.StandardButton.Save |
        QMessageBox.StandardButton.Discard |
        QMessageBox.StandardButton.Cancel,
        QMessageBox.StandardButton.Save)

    if reply == QMessageBox.StandardButton.Cancel:
        return False
    if reply == QMessageBox.StandardButton.Save:
        self.save_file()
        # The Save As dialog may have been cancelled, leaving the document modified.
        return not self.editor.document().isModified()
    return True


def new_file(self):
    if not self.confirm_discard_changes():
        return
    self.editor.clear()
    self.logical_canvas_width = 200
    self.logical_canvas_height = 200
    self.apply_zoom(1.0)
    self.canvas.shapes = []
    self.canvas.update()
    # Use the initial tikz code in the editor when new_file is clicked
    initial_tikz_code_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'initial_tikz_code.tex')
    initial_tikz_code = read_text_file(initial_tikz_code_path)
    self.editor.setPlainText(initial_tikz_code)
    self.editor.document().setModified(False)
    self.current_file_path = None
    self.update_window_title()
    self.original_preview_pixmap = None
    self.preview.clear()
    self.preview.setText("Preview will appear here")
    self.refresh_overlay_layers()

def export_image(self):
    """Export the last compiled drawing as PNG, PDF or SVG (chosen by extension or filter)."""
    import shutil

    temp_dir = getattr(self, 'temp_dir', None)
    pdf_file = os.path.join(temp_dir, "temp.pdf") if temp_dir else None
    png_file = getattr(self, 'image_path', None)
    if not (pdf_file and os.path.exists(pdf_file)) and not (png_file and os.path.exists(png_file)):
        self.output.appendPlainText("\n" + tr("No image to export. Compile first."))
        return

    file_path, selected_filter = QFileDialog.getSaveFileName(
        self, "Save Image", "",
        "PNG Files (*.png);;PDF Files (*.pdf);;SVG Files (*.svg)")
    if not file_path:
        return

    ext = os.path.splitext(file_path)[1].lower()
    if ext not in ('.png', '.pdf', '.svg'):
        # No (or unknown) extension typed: fall back to the selected filter.
        ext = '.pdf' if 'PDF' in selected_filter else '.svg' if 'SVG' in selected_filter else '.png'
        file_path += ext

    try:
        if ext == '.png':
            if not (png_file and os.path.exists(png_file)):
                raise FileNotFoundError("No compiled PNG available. Compile first.")
            shutil.copyfile(png_file, file_path)
        elif pdf_file and os.path.exists(pdf_file):
            if ext == '.pdf':
                shutil.copyfile(pdf_file, file_path)
            else:
                doc = fitz.open(pdf_file)
                try:
                    svg = doc[0].get_svg_image()
                finally:
                    doc.close()
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(svg)
        else:
            raise FileNotFoundError("No compiled PDF available. Fix compilation errors and compile again.")
        self.output.appendPlainText("\n" + tr("Exported to:") + f" {file_path}")
    except Exception as e:
        self.output.appendPlainText("\n" + tr("Export failed:") + f" {e}")

def use_edit_tool(self):
    # Set canvas to selection mode (None indicates we're not in drawing mode)
    self.canvas.drawing_mode = None
    # Reset any arc selection
    self.canvas.arc_selection_state = None
    self.canvas.arc_points = []
    # Reset selection variables
    self.canvas.selected_shape_index = None
    self.canvas.is_selecting = False
    self.canvas.is_dragging = False
    self.canvas.is_editing_point = False  # Reset point editing state
    self.canvas.selected_point_index = None  # Reset selected point
    self.canvas.selection_start = None
    self.canvas.selection_end = None
    # Show appropriate grids for selection/moving
    self.canvas.cartesian_grid_enabled = True
    self.canvas.polar_grid_enabled = False
    # Reset cursor
    self.canvas.setCursor(Qt.CursorShape.ArrowCursor)
    # Update the visual feedback
    self.canvas.update()
    
def use_path_tool(self):
    self.canvas.set_drawing_mode("path")
    self.canvas.cartesian_grid_enabled = True
    self.canvas.polar_grid_enabled = False    
    self.canvas.update()

def use_smooth_curve(self):
    self.canvas.set_drawing_mode("smooth_curve")
    self.canvas.cartesian_grid_enabled = True
    self.canvas.polar_grid_enabled = False    
    self.canvas.update()

def use_rectangle(self):
    self.canvas.set_drawing_mode("rectangle")
    self.canvas.cartesian_grid_enabled = True
    self.canvas.polar_grid_enabled = False    
    self.canvas.update()

def use_circle(self):
    self.canvas.set_drawing_mode("circle")
    self.canvas.cartesian_grid_enabled = True
    self.canvas.polar_grid_enabled = False    
    self.canvas.update()

def use_ellipse(self):
    self.canvas.set_drawing_mode("ellipse")
    self.canvas.cartesian_grid_enabled = True
    self.canvas.polar_grid_enabled = False    
    self.canvas.update()

def use_arc(self):
    self.canvas.set_drawing_mode("arc")
    self.canvas.cartesian_grid_enabled = True
    self.canvas.polar_grid_enabled = False   
    self.canvas.arc_selection_state = "selecting_arc_center"  # New state tracking
    self.canvas.arc_points = []  # Reset arc points
    self.canvas.update()
    
def toggle_overlay(self):
    self.overlay_active = not self.overlay_active
    self.refresh_overlay_layers()


def toggle_grid_visibility(self):
    self.canvas.show_grid = not self.canvas.show_grid
    self.canvas.update()


def toggle_reference_points_visibility(self):
    self.canvas.show_reference_points = not self.canvas.show_reference_points
    self.canvas.update()



def _get_cached_preamble(self):
    """Return the preamble from the memory cache, reading it from disk only on first use or after a save."""
    if not hasattr(self, '_cached_preamble_content') or self._cached_preamble_content is None:
        try:
            header_file_path = app_paths.ensure_user_preamble()
        except OSError:
            # The data folder isn't writable: still work, using the shipped default.
            header_file_path = app_paths.default_preamble_path()
        self._cached_preamble_content = read_text_file(header_file_path)
    return self._cached_preamble_content


def _ensure_temp_dir(self):
    """This session's private temporary folder (created on first use, recreated if it vanished)."""
    if not getattr(self, 'temp_dir', None):
        self.temp_dir = app_paths.new_session_temp_dir()
    else:
        os.makedirs(self.temp_dir, exist_ok=True)
    return self.temp_dir


def _split_preamble(preamble):
    r"""Split preamble.tex into (static, dynamic) parts, or return None if it can't be split.

    static  : everything before the first line that uses a %%PLACEHOLDER%% or
              \pixelwidth/\pixelheight (i.e. \documentclass, packages, libraries).
              It is identical on every compile, so it can be precompiled into a .fmt.
    dynamic : the rest, up to and including \begin{document}%%TIKZ_CODE%%\end{document}.
    """
    doc_idx = preamble.find(r"\begin{document}")
    if doc_idx == -1:
        return None

    split_idx = doc_idx
    m = re.search(r"^.*(?:%%[A-Z_]+%%|\\pixelwidth|\\pixelheight).*$", preamble, re.MULTILINE)
    if m and m.start() < doc_idx:
        split_idx = m.start()

    static = preamble[:split_idx]
    if r"\documentclass" not in static:
        return None
    return static, preamble[split_idx:]


def _extract_latex_errors(log_file, max_errors=5):
    """Return the first LaTeX errors from a .log file as text ('' if none/unreadable).

    LaTeX reports an error as a line starting with '!' followed, a few lines later,
    by 'l.<n> <offending source>'; both lines are kept.
    """
    try:
        with open(log_file, "r", encoding="utf-8", errors="replace") as f:
            lines = f.read().splitlines()
    except OSError:
        return ""

    errors = []
    for i, line in enumerate(lines):
        if not line.startswith("!"):
            continue
        entry = [line]
        for follow in lines[i + 1:i + 8]:
            if follow.startswith("l."):
                entry.append(follow)
                break
        errors.append("\n".join(entry))
        if len(errors) >= max_errors:
            break
    return "\n".join(errors)


def _report_pdflatex_missing(self):
    """Explain once (per configured path) that pdflatex can't be found, instead of on every keystroke."""
    configured = getattr(self, '_pdflatex_path', None)
    key = configured or ''
    if getattr(self, '_pdflatex_missing_reported', None) == key:
        return
    self._pdflatex_missing_reported = key
    if configured:
        message = tr("pdflatex was not found at the path set in Settings:") + f" {configured}"
    else:
        message = tr("pdflatex was not found. Install a TeX distribution (TeX Live, MiKTeX or MacTeX) "
                     "or set the path to pdflatex in Settings.")
    self.output.appendPlainText("\n" + message)


# ---------------------------------------------------------------------------
# Compiling
#
# pdflatex runs in a background QProcess, so the window stays responsive while it
# works (there are no threads: Qt's event loop delivers the "finished" signals).
#
# One compile job runs at a time, in up to three stages:
#   1. build the precompiled format, if the static part of the preamble changed
#   2. run pdflatex
#   3. rasterise the PDF and update the preview/canvas (fast, on the UI thread)
#
# A compile request that arrives while a job is running supersedes it: the running
# pdflatex is stopped and a new job starts on the newest editor text. A format build
# is never interrupted (that would leave a half-written cache file); the newest
# request simply starts as soon as it is done.
#
# Each job works on its own uniquely named files (build<N>.*) and publishes
# temp.pdf / temp.tex / temp.log only when it finishes, so the last good PDF stays
# available to Export and "Show PDF" while newer jobs are running.
# ---------------------------------------------------------------------------

COMPILE_TIMEOUT_MS = 120_000
FORMAT_TIMEOUT_MS = 30_000
BUSY_INDICATOR_DELAY_MS = 300     # "Compiling..." appears only if a compile takes longer than this


def _new_process(self, program, arguments, cwd, env):
    """Create (but don't start) a QProcess for a TeX run. Also the seam tests use to observe or replace runs."""
    process = QProcess(self)
    process.setProgram(program)
    process.setArguments(list(arguments))
    process.setWorkingDirectory(cwd)
    qt_env = QProcessEnvironment()
    for key, value in env.items():
        qt_env.insert(key, value)
    process.setProcessEnvironment(qt_env)
    # pdflatex's console output is not used (the .log file is); discard it instead of buffering it.
    process.setStandardOutputFile(QProcess.nullDevice())
    process.setStandardErrorFile(QProcess.nullDevice())
    return process


def _launch(self, process, timeout_ms, on_done):
    """Start `process`; call on_done(exit_code, crashed, timed_out, start_failed) exactly once when it ends."""
    state = {"done": False, "timed_out": False}
    timeout = QTimer(process)
    timeout.setSingleShot(True)
    timeout.setInterval(timeout_ms)

    def finish(exit_code, crashed, start_failed=False):
        if state["done"]:
            return
        state["done"] = True
        timeout.stop()
        process.deleteLater()
        on_done(exit_code, crashed, state["timed_out"], start_failed)

    def on_timeout():
        state["timed_out"] = True
        process.kill()

    timeout.timeout.connect(on_timeout)
    process.finished.connect(
        lambda code, status: finish(code, status == QProcess.ExitStatus.CrashExit))
    process.errorOccurred.connect(
        lambda error: finish(-1, False, True) if error == QProcess.ProcessError.FailedToStart else None)
    timeout.start()
    process.start()


def is_compile_idle(self):
    """True when no compile is running or about to start."""
    return getattr(self, '_compile_job', None) is None and not getattr(self, '_restart_scheduled', False)


def wait_for_compile(self, timeout_ms=120_000):
    """Process events until the compile is finished. Returns False if it timed out.
    For tests and scripts; the UI itself never blocks on a compile."""
    if is_compile_idle(self):
        return True
    loop = QEventLoop()
    poll = QTimer()
    poll.setInterval(10)
    poll.timeout.connect(lambda: loop.quit() if is_compile_idle(self) else None)
    give_up = QTimer()
    give_up.setSingleShot(True)
    give_up.timeout.connect(loop.quit)
    poll.start()
    give_up.start(timeout_ms)
    loop.exec()
    poll.stop()
    give_up.stop()
    return is_compile_idle(self)


def compile_and_wait(self, timeout_ms=120_000):
    """compile_tikz(), then wait for it to finish."""
    self.compile_tikz()
    return wait_for_compile(self, timeout_ms)


def _prepare_compile_job(self, t_start):
    """Work out everything a compile needs from the current editor state (no files are touched).
    Returns None if pdflatex can't be found."""
    tikz_code = self.editor.toPlainText()
    tikz_code_for_compile = self.parser._ensure_tikzpicture(tikz_code)

    # This session's private temp folder (created on first use)
    _ensure_temp_dir(self)

    # Optimization #4: Use cached preamble content instead of reading from disk every time
    header_content = self._get_cached_preamble()

    # Convert tight bounding box to TeX points for the preamble
    # 1cm = 28.4527559 pt.
    pts_per_cm = 28.4527559

    # Calculate tight bounding box directly from shapes (independent X and Y)
    max_extent_x = 50  # minimum extent padding
    max_extent_y = 50
    if self.canvas.shapes:
        for shape in self.canvas.shapes:
            shape_points = shape[:-1]
            if not shape_points: continue
            shape_max_x = max(abs(p.x()) for p in shape_points)
            shape_max_y = max(abs(p.y()) for p in shape_points)
            max_extent_x = max(max_extent_x, shape_max_x)
            max_extent_y = max(max_extent_y, shape_max_y)

    # Add padding to extents
    max_extent_x += 50
    max_extent_y += 50
    computed_pdf_logical_width = max(200, max_extent_x * 2)
    computed_pdf_logical_height = max(200, max_extent_y * 2)

    pixel_width_pt = (computed_pdf_logical_width / self.parser.scaling) * pts_per_cm
    pixel_height_pt = (computed_pdf_logical_height / self.parser.scaling) * pts_per_cm

    tex_content = header_content.replace("%%TIKZ_CODE%%", tikz_code_for_compile)
    tex_content = tex_content.replace("%%PIXEL_WIDTH%%", str(pixel_width_pt))
    tex_content = tex_content.replace("%%PIXEL_HEIGHT%%", str(pixel_height_pt))
    content_hash = hashlib.md5(tex_content.encode()).hexdigest()

    pdflatex = find_pdflatex(getattr(self, '_pdflatex_path', None))
    if pdflatex is None:
        _report_pdflatex_missing(self)
        return None
    self._pdflatex_missing_reported = None

    # Optimization #1: precompile the static part of the preamble (packages, libraries).
    # The rest of the file is compiled normally, so both paths honour whatever is in the preamble.
    static = fmt_tex_body = static_hash = None
    split = _split_preamble(header_content)
    if split is not None and tex_content.startswith(split[0]):
        static = split[0]
        fmt_tex_body = tex_content[len(static):]
        static_hash = hashlib.md5(static.encode()).hexdigest()

    return SimpleNamespace(
        t_start=t_start, tex_content=tex_content, content_hash=content_hash,
        pixel_width_pt=pixel_width_pt, pixel_height_pt=pixel_height_pt,
        pdflatex=pdflatex, static=static, static_hash=static_hash, fmt_tex_body=fmt_tex_body,
        stage="", process=None, cancel_reason=None, used_fmt=False,
        t_latex=None, t_latex_done=None,
        name="", tex_file="", pdf_file="", log_file="")


def compile_tikz(self, update_shapes=True):
    """Compile the current TikZ code in the background.

    Returns immediately; the preview and canvas update when pdflatex has finished.
    If a compile is already running, the newest request replaces it.
    """
    if getattr(self, '_closing', False):
        return
    self._restart_scheduled = False
    t_start = time.time()
    self.timer.stop()

    job = _prepare_compile_job(self, t_start)
    if job is None:
        return

    running = getattr(self, '_compile_job', None)
    if running is None:
        # Optimization #6: skip compilation if the tex content is identical to the last compiled one
        if job.content_hash == getattr(self, '_last_compiled_hash', ''):
            print(f"Compilation skipped (unchanged) in {time.time() - t_start:.3f}s")
            return
        _run_job(self, job)
        return

    if job.content_hash == running.content_hash:
        return                                    # exactly this is already being compiled
    self._compile_pending = True                  # newest text wins: start over once the running job ends
    if running.stage == "compile" and running.process is not None:
        running.cancel_reason = "superseded"
        running.process.kill()
    # A format build is left to finish; the pending request starts right after it.


def _remove_quietly(path):
    try:
        os.remove(path)
    except OSError:
        pass


def _run_job(self, job):
    self._job_counter = getattr(self, '_job_counter', 0) + 1
    job.name = f"build{self._job_counter}"
    job.tex_file = os.path.join(self.temp_dir, job.name + ".tex")
    job.pdf_file = os.path.join(self.temp_dir, job.name + ".pdf")
    job.log_file = os.path.join(self.temp_dir, job.name + ".log")
    self._compile_job = job
    self._compile_pending = False
    _show_busy_soon(self)

    try:
        with open(job.tex_file, "w", encoding="utf-8") as f:
            f.write(job.tex_content)
    except OSError as e:
        self.output.appendPlainText("\n" + tr("Could not write the temporary file:") + f" {e}")
        _end_job(self)
        return

    fmt_file = os.path.join(self.temp_dir, "tikz_preamble.fmt")
    if job.static_hash is None:
        _start_pdflatex(self, job, None)                          # no precompilable part
    elif getattr(self, '_fmt_static_hash', None) == job.static_hash and os.path.exists(fmt_file):
        _start_pdflatex(self, job, fmt_file)                      # format is up to date
    elif getattr(self, '_fmt_failed_hash', None) == job.static_hash:
        _start_pdflatex(self, job, None)                          # building it failed before; don't retry
    else:
        _start_format_build(self, job, fmt_file)


def _start_format_build(self, job, fmt_file):
    r"""Build the precompiled format from the static part of the preamble (background).

    Precompiling \documentclass, the packages and TikZ libraries means pdflatex doesn't
    re-parse them on every run. The format is rebuilt whenever the static part changes,
    so edits made in the Preamble tab take effect. If building fails (e.g. a missing
    package) the failure is reported once and compiles go on without a format.
    """
    job.stage = "format"
    job.fmt_path = fmt_file
    # A format built from an older preamble must never survive a failed rebuild.
    self._fmt_static_hash = None
    try:
        if os.path.exists(fmt_file):
            os.remove(fmt_file)
        dump_tex = os.path.join(self.temp_dir, "tikz_preamble_dump.tex")
        with open(dump_tex, "w", encoding="utf-8") as f:
            f.write(job.static.rstrip() + "\n\\dump\n")
    except OSError as e:
        print(f"Could not prepare the format build: {e}")
        self._fmt_failed_hash = job.static_hash
        _start_pdflatex(self, job, None)
        return

    process = _new_process(
        self, job.pdflatex,
        ["-ini", "-no-shell-escape", "-interaction=nonstopmode", "-jobname=tikz_preamble", "&pdflatex", dump_tex],
        self.temp_dir, subprocess_env(job.pdflatex))
    job.process = self.compilation_process = process
    _launch(self, process, FORMAT_TIMEOUT_MS,
            lambda code, crashed, timed_out, start_failed:
            _on_format_built(self, job, code, crashed, timed_out, start_failed))


def _on_format_built(self, job, exit_code, crashed, timed_out, start_failed):
    job.process = self.compilation_process = None
    fmt_file = job.fmt_path
    built = (os.path.exists(fmt_file) and not (crashed or timed_out or start_failed or job.cancel_reason))
    if not built:
        _remove_quietly(fmt_file)                     # never leave a partial format behind

    if job.cancel_reason == "user":
        self._fmt_static_hash = None
        _end_job(self)
        return

    if built:
        self._fmt_static_hash = job.static_hash
        self._fmt_failed_hash = None
        print(f"Format file created: {fmt_file}")
    else:
        if start_failed:
            reason = tr("Could not start pdflatex:") + f" {job.pdflatex}"
        elif timed_out:
            reason = tr("Compilation timed out.")
        else:
            reason = _extract_latex_errors(os.path.join(self.temp_dir, "tikz_preamble.log"))
        print(f"Format file generation failed (exit code {exit_code})")
        self._fmt_failed_hash = job.static_hash
        self.output.appendPlainText(
            "\n" + tr("Could not precompile the preamble; compiling without the format cache.") +
            (("\n" + reason) if reason else ""))

    if self._compile_pending:
        _end_job(self)                                # a newer request is waiting: start it now
        return
    _start_pdflatex(self, job, fmt_file if built else None)


def _start_pdflatex(self, job, fmt_file):
    job.stage = "compile"
    job.used_fmt = bool(fmt_file)
    if fmt_file:
        # The per-run file is the dynamic remainder of the preamble (already filled with the
        # page size and TikZ code) minus the precompiled part.
        run_file = os.path.join(self.temp_dir, job.name + "_fmt.tex")
        try:
            with open(run_file, "w", encoding="utf-8") as f:
                f.write("\\pdfcompresslevel=0\n\\pdfobjcompresslevel=0\n" + job.fmt_tex_body)
        except OSError as e:
            self.output.appendPlainText("\n" + tr("Could not write the temporary file:") + f" {e}")
            _end_job(self)
            return
        arguments = ["-no-shell-escape", "-interaction=batchmode",
                     f"-fmt={os.path.splitext(fmt_file)[0]}",
                     "-output-directory", self.temp_dir, f"-jobname={job.name}", run_file]
    else:
        arguments = ["-no-shell-escape", "-interaction=batchmode",
                     "-output-directory", self.temp_dir, job.tex_file]

    process = _new_process(self, job.pdflatex, arguments, self.temp_dir, subprocess_env(job.pdflatex))
    job.process = self.compilation_process = process
    job.t_latex = time.time()
    _launch(self, process, COMPILE_TIMEOUT_MS,
            lambda code, crashed, timed_out, start_failed:
            _on_pdflatex_done(self, job, code, crashed, timed_out, start_failed))


def _publish(self, job, *kinds):
    """Make this job's files the current temp.<kind> (atomically where possible)."""
    for kind in kinds:
        source = getattr(job, kind + "_file")
        if not os.path.exists(source):
            continue
        target = os.path.join(self.temp_dir, "temp." + kind)
        try:
            os.replace(source, target)
        except OSError:
            try:
                shutil.copyfile(source, target)
            except OSError as e:
                print(f"Could not publish {target}: {e}")


def _on_pdflatex_done(self, job, exit_code, crashed, timed_out, start_failed):
    job.t_latex_done = time.time()
    job.process = self.compilation_process = None
    try:
        if job.cancel_reason == "user":
            return
        if job.cancel_reason == "superseded" or self._compile_pending:
            return                                    # a newer request replaces this result
        if start_failed:
            self.output.appendPlainText(
                "\n" + tr("Could not start pdflatex:") + f" {job.pdflatex}")
        elif timed_out:
            _publish(self, job, "tex", "log")
            self.output.appendPlainText("\n" + tr("Compilation timed out."))
        else:
            _finish_compile(self, job, exit_code)
    finally:
        _end_job(self)


def _finish_compile(self, job, returncode):
    """Show the result of a finished pdflatex run (UI thread)."""
    published_pdf = os.path.join(self.temp_dir, "temp.pdf")
    published_log = os.path.join(self.temp_dir, "temp.log")
    published_tex = os.path.join(self.temp_dir, "temp.tex")

    if not os.path.exists(job.pdf_file):
        # pdflatex produced nothing: keep the previous preview (and last good PDF), report why,
        # and leave the hash unset so the next compile retries.
        errors = _extract_latex_errors(job.log_file)
        _publish(self, job, "tex", "log")
        self.output.setPlainText(
            self.output.toPlainText() +
            f"\n\n{tr('Compilation failed.')} (pdflatex exit code {returncode})\n" +
            (errors + "\n" if errors else "") +
            f"{tr('Log file:')} {published_log}\n"
        )
        return
    compile_had_errors = returncode != 0
    latex_errors = _extract_latex_errors(job.log_file) if compile_had_errors else ""

    # Using PyMuPDF to convert the pdf to an image with a transparent background
    t_raster = job.t_latex_done
    try:
        doc = fitz.open(job.pdf_file)
        try:
            page = doc[0]
            # 600 DPI is a scale of 600/72 = 8.333
            matrix = fitz.Matrix(8.333, 8.333)
            pix = page.get_pixmap(matrix=matrix, alpha=True)
        finally:
            # Release the file handle: Windows can't replace an open PDF.
            doc.close()
        t_raster = time.time()

        self.image_path = os.path.join(self.temp_dir, "output.png")
        pix.save(self.image_path)

        # Load the pixmap and store it.
        pixmap = QPixmap(self.image_path)
        if not pixmap.isNull():
            self.original_preview_pixmap = pixmap  # Store the original pixmap for future scaling
            self.preview.setPixmap(pixmap)
            self.preview.update()
            self.canvas.update()

            # IMPORTANT: Synchronize the parser's scaling with the physical size of the PDF
            # to keep the logical widget size reasonably small instead of matching high-DPI pixels.
            pts_per_cm = 28.4527559
            actual_pdf_width_pt = job.pixel_width_pt * getattr(self.parser, 'tikz_scale', 1.0)
            actual_pdf_height_pt = job.pixel_height_pt * getattr(self.parser, 'tikz_scale', 1.0)

            # Standard screen is ~96 DPI. Calculate physical widget size based on 96 DPI:
            target_logical_width = max(200, int(actual_pdf_width_pt * (96.0 / 72.0)))
            target_logical_height = max(200, int(actual_pdf_height_pt * (96.0 / 72.0)))

            # New scaling maps logical screen pixels to cm
            new_scaling = (target_logical_width / actual_pdf_width_pt) * pts_per_cm

            self.parser.scaling = new_scaling
            # Save the PDF logical size for the preview
            self.pdf_logical_width = target_logical_width
            self.pdf_logical_height = target_logical_height

            # --- Dynamic canvas sizing  ---
            # Update the logical canvas dimensions to match the content extent,
            # clamped to reasonable bounds. This makes the scrollable area
            # grow/shrink with the drawn objects.
            MIN_CANVAS = 200
            MAX_CANVAS = 4000
            self.logical_canvas_width = max(MIN_CANVAS, min(MAX_CANVAS, target_logical_width))
            self.logical_canvas_height = max(MIN_CANVAS, min(MAX_CANVAS, target_logical_height))

            self.apply_zoom(self.preview_scale)
            self.refresh_overlay_layers()
            # Optimization #5: Single parse pass after compilation instead of
            # invalidate_cache() + parse (which forced two full ANTLR parses).
            # The scaling just changed, so we invalidate and do one fresh parse.
            self.parser.invalidate_cache()
            self.parse_tikz_and_update_canvas()
        else:
            self.preview.setText("Failed to load image.")
    except Exception as e:
        print(f"Rasterization error: {e}")
        self.preview.setText("Failed to load image.")

    _publish(self, job, "pdf", "tex", "log")

    # Optimization #6: Store hash of successfully compiled content.
    # Runs that reported LaTeX errors are not cached, so they are retried.
    if not compile_had_errors:
        self._last_compiled_hash = job.content_hash

    # Display the compilation output with timing info
    t_end = time.time()
    if compile_had_errors:
        status_text = (
            f"{tr('Compiled with errors (showing partial output).')} "
            f"(pdflatex exit code {returncode})\n"
            f"{latex_errors}\n"
        )
    else:
        status_text = f"{tr('Compilation successful.')} "
    compilation_text = (
        f"\n\n{status_text}"
        f"(total: {t_end - job.t_start:.2f}s, "
        f"pdflatex: {job.t_latex_done - job.t_latex:.2f}s, "
        f"raster: {t_raster - job.t_latex_done:.2f}s, "
        f"fmt: {'yes' if job.used_fmt else 'no'}).\n"
        f"{tr('Temporary files located at:')} {self.temp_dir}\n"
        f"{tr('tex file:')} {published_tex}\n"
        f"{tr('pdf file:')} {published_pdf}\n"
    )
    self.output.setPlainText(self.output.toPlainText() + compilation_text)


def _end_job(self):
    """Finish the current job's bookkeeping and start the newest waiting request, if any."""
    job = getattr(self, '_compile_job', None)
    self._compile_job = None
    self.compilation_process = None
    if job is not None and job.name:
        # exact patterns: "build1*" would also match the files of build10, build11...
        for pattern in (job.name + ".*", job.name + "_*"):
            for leftover in glob.glob(os.path.join(glob.escape(self.temp_dir), pattern)):
                _remove_quietly(leftover)
    _clear_busy(self)
    if getattr(self, '_compile_pending', False) and not getattr(self, '_closing', False):
        self._compile_pending = False
        self._restart_scheduled = True
        QTimer.singleShot(0, lambda: compile_tikz(self))


def cancel_compilation(self):
    """Stop the running compilation (Cancel button / Abort menu)."""
    job = getattr(self, '_compile_job', None)
    if job is None:
        return
    self._compile_pending = False
    job.cancel_reason = "user"
    self.output.appendPlainText("\n" + tr("Compilation cancelled by user."))
    if job.process is not None:
        job.process.kill()                            # its "finished" signal ends the job
    else:
        _end_job(self)


def shutdown_compilation(self):
    """Stop everything before the window closes, so the temp folder can be deleted."""
    self._closing = True
    self._compile_pending = False
    self.timer.stop()
    job = getattr(self, '_compile_job', None)
    if job is None:
        return
    job.cancel_reason = "user"
    if job.process is not None:
        job.process.kill()
        job.process.waitForFinished(3000)
    if getattr(self, '_compile_job', None) is not None:
        _end_job(self)


# --- "Compiling..." indicator: shown only when a compile takes noticeably long ---

def _show_busy_soon(self):
    timer = getattr(self, '_busy_timer', None)
    if timer is None:
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: _show_busy_now(self))
        self._busy_timer = timer
    timer.start(BUSY_INDICATOR_DELAY_MS)


def _show_busy_now(self):
    if getattr(self, '_compile_job', None) is not None:
        bar = self.statusBar()
        bar.showMessage(tr("Compiling..."))
        bar.setVisible(True)
        self._busy_message_shown = True


def _clear_busy(self):
    timer = getattr(self, '_busy_timer', None)
    if timer is not None:
        timer.stop()
    if getattr(self, '_busy_message_shown', False):
        self._busy_message_shown = False
        self.statusBar().clearMessage()
        if hasattr(self, 'update_parse_status'):
            self.update_parse_status()                # bring back (or hide) the canvas-overlay message


def _replace_editor_text(editor, new_text, join_previous=False):
    """Make the editor's text equal to new_text by replacing only the span that differs.

    Done as one edit block on the document, so it is a single undo step (or is merged
    into the previous undo step when join_previous is True) and does not reset the
    editor's cursor, selection, scroll position or undo history.
    """
    old_text = editor.toPlainText()
    if old_text == new_text:
        return

    # Common prefix / suffix; the middle of each string is what actually changed.
    limit = min(len(old_text), len(new_text))
    start = 0
    while start < limit and old_text[start] == new_text[start]:
        start += 1
    end = 0
    while end < limit - start and old_text[-1 - end] == new_text[-1 - end]:
        end += 1

    def utf16_len(s):
        # QTextDocument positions count UTF-16 code units, Python indexes code points.
        return len(s.encode("utf-16-le")) // 2

    from_pos = utf16_len(old_text[:start])
    to_pos = from_pos + utf16_len(old_text[start:len(old_text) - end])

    cursor = QTextCursor(editor.document())
    if join_previous:
        cursor.joinPreviousEditBlock()
    else:
        cursor.beginEditBlock()
    try:
        cursor.setPosition(from_pos)
        cursor.setPosition(to_pos, QTextCursor.MoveMode.KeepAnchor)
        cursor.insertText(new_text[start:len(new_text) - end])
    finally:
        cursor.endEditBlock()


def update_tikz_code(self):
    # Set flag to prevent feedback loop
    self.updating_from_canvas = True
    
    try:
        # Use the code from the last time it was parsed as the baseline.
        # This prevents character offsets from shifting when dragging shapes continuously.
        old_code = getattr(self.parser, 'last_code', "")
        if not old_code:
            old_code = self.editor.toPlainText()
        
        # First, match newly drawn shapes with existing parsed shapes to copy intervals
        # This ensures updates go to existing code instead of appending new commands
        # Only match shapes that are marked as newly drawn (not all shapes)
        parsed_shapes = getattr(self.parser, 'last_parsed_shapes', [])
        newly_drawn_indices = getattr(self.canvas, 'newly_drawn_indices', set())
        
        has_newly_drawn = len(newly_drawn_indices) > 0
        
        if parsed_shapes and newly_drawn_indices:
            self.canvas.shapes = self.parser.match_intervals_for_drawn_shapes(
                self.canvas.shapes, 
                parsed_shapes,
                newly_drawn_indices
            )
        
        # Delegate the actual string replacement and formatting to the parser
        deleted_cmd_intervals = getattr(self.canvas, 'deleted_cmd_intervals', [])
        tikz_code = self.parser.update_code(
            old_code, 
            self.canvas.shapes, 
            scale_factor=self.canvas.scale_factor,
            deleted_cmd_intervals=deleted_cmd_intervals
        )
        self.canvas.deleted_cmd_intervals = []
        
        is_final_update = (
            not self.canvas.is_dragging and
            not getattr(self.canvas, 'is_editing_point', False) and
            not getattr(self.canvas, 'is_dragging_overlay_node', False) and
            not getattr(self.canvas, 'is_dragging_overlay_scope', False)
        )

        # Block signals before updating the text to prevent feedback loop
        self.editor.blockSignals(True)
        # Edit the document in place (instead of setPlainText) so the editor's undo history,
        # cursor and scroll position survive. All updates of one drag gesture are merged
        # into a single undo step.
        _replace_editor_text(self.editor, tikz_code,
                             join_previous=getattr(self, '_canvas_edit_open', False))
        self._canvas_edit_open = not (is_final_update or has_newly_drawn)
        self.editor_highlighter.rehighlight()

        # If we had newly drawn shapes, parse the updated code to get proper intervals assigned
        if has_newly_drawn:
            # Parse the newly updated TikZ code to assign intervals to the shapes
            updated_canvas_shapes = self.parser.parse_to_canvas_shapes(tikz_code, incremental=False)
            if updated_canvas_shapes:
                self.canvas.shapes = updated_canvas_shapes
                self.canvas.overlay_model = getattr(self.parser, 'last_overlay_model', {'nodes': [], 'scopes': []})
            # Clear the newly drawn indices now that they have been processed
            self.canvas.newly_drawn_indices = set()
            is_final_update = True
        elif is_final_update:
            # If this is the final update (not a continuous drag), refresh the parser
            # to get new intervals and update the baseline 'last_code'.
            self.updating_from_canvas = False
            self.parse_tikz_and_update_canvas()
            self.updating_from_canvas = True
            
        if is_final_update:
            # Automatically trigger compilation after dragging/drawing finishes
            self.timer.stop()
            self.timer.start()
        

        
    finally:
        # Always restore signals and reset our flag
        self.editor.blockSignals(False)
        self.updating_from_canvas = False
