from PyQt6.QtWidgets import QMenuBar
from PyQt6.QtGui import QAction, QKeySequence
import os
from zTikz.utils.translations import tr, set_language
from zTikz.utils.theme import get_icon

def create_menu(main_window):
    menu_bar = QMenuBar(main_window)
    icons_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons')
    
    # File menu
    file_menu = menu_bar.addMenu(tr("File"))
    new_action = QAction(get_icon('new.svg'), tr("New"), main_window)
    new_action.setShortcut(QKeySequence.StandardKey.New)
    new_action.triggered.connect(main_window.new_file)
    open_action = QAction(get_icon('open.svg'), tr("Open"), main_window)
    open_action.setShortcut(QKeySequence.StandardKey.Open)
    open_action.triggered.connect(main_window.open_file)
    save_action = QAction(get_icon('save.svg'), tr("Save"), main_window)
    save_action.setShortcut(QKeySequence.StandardKey.Save)
    save_action.triggered.connect(main_window.save_file)
    save_as_action = QAction(tr("Save As..."), main_window)
    save_as_action.triggered.connect(main_window.save_as_file)
    export_action = QAction(get_icon('export.svg'), tr("Export"), main_window)
    export_action.triggered.connect(main_window.export_image)
    
    file_menu.addAction(new_action)
    file_menu.addAction(open_action)
    file_menu.addAction(save_action)
    file_menu.addAction(save_as_action)
    file_menu.addAction(export_action)
    file_menu.addSeparator()
    exit_action = QAction(tr("Exit"), main_window)
    exit_action.triggered.connect(main_window.close)
    file_menu.addAction(exit_action)

    # Edit menu
    edit_menu = menu_bar.addMenu(tr("Edit"))

    undo_action = QAction(tr("Undo"), main_window)
    undo_action.setShortcut(QKeySequence.StandardKey.Undo)
    undo_action.triggered.connect(lambda: _active_editor(main_window).undo())
    edit_menu.addAction(undo_action)

    redo_action = QAction(tr("Redo"), main_window)
    redo_action.setShortcut(QKeySequence.StandardKey.Redo)
    redo_action.triggered.connect(lambda: _active_editor(main_window).redo())
    edit_menu.addAction(redo_action)

    edit_menu.addSeparator()

    cut_action = QAction(tr("Cut"), main_window)
    cut_action.setShortcut(QKeySequence.StandardKey.Cut)
    cut_action.triggered.connect(lambda: _active_editor(main_window).cut())
    edit_menu.addAction(cut_action)

    copy_action = QAction(tr("Copy"), main_window)
    copy_action.setShortcut(QKeySequence.StandardKey.Copy)
    copy_action.triggered.connect(lambda: _active_editor(main_window).copy())
    edit_menu.addAction(copy_action)

    paste_action = QAction(tr("Paste"), main_window)
    paste_action.setShortcut(QKeySequence.StandardKey.Paste)
    paste_action.triggered.connect(lambda: _active_editor(main_window).paste())
    edit_menu.addAction(paste_action)

    edit_menu.addSeparator()

    find_replace_action = QAction(tr("Find and Replace"), main_window)
    find_replace_action.setShortcut(QKeySequence.StandardKey.Find)
    find_replace_action.triggered.connect(lambda: _show_find_dialog(main_window))
    edit_menu.addAction(find_replace_action)

    find_next_action = QAction(tr("Find Next"), main_window)
    find_next_action.setShortcut(QKeySequence.StandardKey.FindNext)
    find_next_action.triggered.connect(lambda: _find_next(main_window))
    edit_menu.addAction(find_next_action)

    edit_menu.addSeparator()

    comment_action = QAction(tr("Comment/Uncomment"), main_window)
    comment_action.setShortcut("Ctrl+/")
    comment_action.triggered.connect(lambda: _active_editor(main_window).toggle_comment())
    edit_menu.addAction(comment_action)

    # View menu
    view_menu = menu_bar.addMenu(tr("View"))

    show_pdf_action = QAction(get_icon('show_pdf.svg'), tr("Show PDF in external viewer"), main_window)
    show_pdf_action.triggered.connect(lambda: _open_pdf_externally(main_window))
    view_menu.addAction(show_pdf_action)

    view_menu.addSeparator()

    def toggle_word_wrap(checked):
        from PyQt6.QtWidgets import QPlainTextEdit
        mode = QPlainTextEdit.LineWrapMode.WidgetWidth if checked else QPlainTextEdit.LineWrapMode.NoWrap
        main_window.editor.setLineWrapMode(mode)
        main_window.preamble_editor.setLineWrapMode(mode)

    word_wrap_action = QAction(tr("Word Wrap"), main_window)
    word_wrap_action.setCheckable(True)
    word_wrap_action.setChecked(False)
    word_wrap_action.toggled.connect(toggle_word_wrap)
    view_menu.addAction(word_wrap_action)

    from PyQt6.QtGui import QActionGroup
    
    theme_menu = view_menu.addMenu(tr("Theme"))
    theme_group = QActionGroup(main_window)
    
    light_mode_action = QAction(tr("Light mode"), main_window)
    light_mode_action.setCheckable(True)
    theme_group.addAction(light_mode_action)
    theme_menu.addAction(light_mode_action)
    
    dark_mode_action = QAction(tr("Dark mode"), main_window)
    dark_mode_action.setCheckable(True)
    theme_group.addAction(dark_mode_action)
    theme_menu.addAction(dark_mode_action)

    def set_theme(action):
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QSettings
        from zTikz.utils.theme import set_dark_mode
        
        is_dark = (action == dark_mode_action)
        main_window._dark_mode = is_dark
        
        settings = QSettings('zTikz', 'zTikz')
        settings.setValue('dark_mode', is_dark)
        
        app = QApplication.instance()
        if app:
            set_dark_mode(app, is_dark)
            
        # Re-initialize highlighters
        main_window.editor_highlighter.load_highlighting_settings()
        main_window.editor_highlighter.rehighlight()
        
        main_window.preamble_highlighter.load_highlighting_settings()
        main_window.preamble_highlighter.rehighlight()
        
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(main_window, tr("Theme Changed"), tr("The theme has been changed. Please restart the application for all icons to update."))

    theme_group.triggered.connect(set_theme)
    
    # We no longer need to call set_theme(dark_mode_action) here because it was already called
    # in main_window.__init__ before the UI was built. We just set the check state.
    is_dark = getattr(main_window, '_dark_mode', False)
    if is_dark:
        dark_mode_action.setChecked(True)
    else:
        light_mode_action.setChecked(True)

    # Compilation menu
    compilation_menu = menu_bar.addMenu(tr("Compilation"))

    compile_action = QAction(get_icon('compile.svg'), tr("Compile"), main_window)
    compile_action.setShortcut("F5")
    compile_action.triggered.connect(main_window.compile_tikz)
    compilation_menu.addAction(compile_action)

    abort_action = QAction(get_icon('cancel.svg'), tr("Abort"), main_window)
    abort_action.triggered.connect(main_window.cancel_compilation)
    compilation_menu.addAction(abort_action)

    compilation_menu.addSeparator()

    def set_auto_compile(checked):
        main_window.auto_compile_enabled = checked

    auto_compile_action = QAction(get_icon('auto_compile.svg'), tr("Auto compilation on code change"), main_window)
    auto_compile_action.setCheckable(True)
    auto_compile_action.setChecked(True)
    auto_compile_action.toggled.connect(set_auto_compile)
    compilation_menu.addAction(auto_compile_action)

    compilation_menu.addSeparator()

    recompile_snippets_action = QAction(tr("Re-compile the Snippets thumbnails"), main_window)
    recompile_snippets_action.triggered.connect(main_window.recompile_snippets)
    compilation_menu.addAction(recompile_snippets_action)

    # Settings — clicking the menu title directly opens the settings dialog
    settings_action = QAction(tr("Settings"), main_window)
    settings_action.triggered.connect(lambda: _show_settings_dialog(main_window))
    menu_bar.addAction(settings_action)

    # Help menu
    help_menu = menu_bar.addMenu(tr("Help"))

    check_updates_action = QAction(tr("Check for Updates"), main_window)
    check_updates_action.triggered.connect(lambda: _open_url("https://paulomarconi.github.io"))
    help_menu.addAction(check_updates_action)

    help_menu.addSeparator()

    about_action = QAction(tr("About"), main_window)
    about_action.triggered.connect(lambda: _show_about_dialog(main_window))
    help_menu.addAction(about_action)
    
    return menu_bar


def _open_pdf_externally(main_window):
    """Open a copy of the last compiled PDF in the system's default PDF viewer.

    A copy is opened rather than temp.pdf itself: some viewers lock the file they show,
    which would stop the next compile from replacing it.
    """
    import os
    import shutil
    import time
    from PyQt6.QtCore import QUrl
    from PyQt6.QtGui import QDesktopServices

    temp_dir = getattr(main_window, 'temp_dir', None)
    pdf_path = os.path.join(temp_dir, 'temp.pdf') if temp_dir else None
    if not (pdf_path and os.path.exists(pdf_path)):
        main_window.output.appendPlainText(tr("No compiled PDF found. Compile first."))
        return

    viewer_copy = os.path.join(temp_dir, 'viewer_copy.pdf')
    try:
        shutil.copyfile(pdf_path, viewer_copy)
    except OSError:
        # The previous copy is still open (locked) in a viewer: use a fresh file name.
        viewer_copy = os.path.join(temp_dir, f'viewer_copy_{time.time_ns()}.pdf')
        try:
            shutil.copyfile(pdf_path, viewer_copy)
        except OSError as e:
            main_window.output.appendPlainText("\n" + tr("Could not open the PDF:") + f" {e}")
            return

    viewer = getattr(main_window, '_pdf_viewer_path', None)
    if viewer:
        if _start_viewer(viewer, viewer_copy):
            return
        main_window.output.appendPlainText(
            "\n" + tr("Could not start the PDF viewer set in Settings; using the system default:") + f" {viewer}")

    if not QDesktopServices.openUrl(QUrl.fromLocalFile(viewer_copy)):
        main_window.output.appendPlainText("\n" + tr("Could not open the PDF:") + f" {viewer_copy}")


def _start_viewer(viewer, pdf_file):
    """Start the user's chosen PDF viewer on pdf_file. Returns False if it can't be started."""
    import sys
    from PyQt6.QtCore import QProcess

    viewer = os.path.expanduser(viewer.strip().strip('"'))
    if sys.platform == 'darwin' and viewer.endswith('.app') and os.path.isdir(viewer):
        program, arguments = 'open', ['-a', viewer, pdf_file]          # macOS application bundle
    elif os.path.isfile(viewer):
        program, arguments = viewer, [pdf_file]
    else:
        return False
    result = QProcess.startDetached(program, arguments)
    return result[0] if isinstance(result, tuple) else bool(result)


def _active_editor(main_window):
    """Return whichever editor (code or preamble) currently has focus."""
    if hasattr(main_window, 'preamble_editor') and main_window.preamble_editor.hasFocus():
        return main_window.preamble_editor
    return main_window.editor


def _show_find_dialog(main_window):
    """Show the floating Find and Replace dialog."""
    from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel
    from PyQt6.QtCore import Qt

    # If the dialog already exists, just show it and focus
    if hasattr(main_window, '_find_dialog') and main_window._find_dialog is not None:
        main_window._find_dialog.show()
        main_window._find_dialog.raise_()
        main_window._find_dialog.activateWindow()
        main_window._find_input.selectAll()
        main_window._find_input.setFocus()
        return

    # Build the find/replace dialog
    dialog = QDialog(main_window)
    dialog.setWindowTitle(tr("Find and Replace"))
    
    # We don't want it to be modal because the user needs to interact with the text while the dialog is open
    dialog.setModal(False)
    
    layout = QVBoxLayout(dialog)

    # Find row
    find_layout = QHBoxLayout()
    find_label = QLabel(tr("Find:"))
    find_input = QLineEdit()
    find_input.setPlaceholderText("Search...")
    find_layout.addWidget(find_label)
    find_layout.addWidget(find_input)
    layout.addLayout(find_layout)

    # Replace row
    replace_layout = QHBoxLayout()
    replace_label = QLabel(tr("Replace:"))
    replace_input = QLineEdit()
    replace_input.setPlaceholderText("Replace with...")
    replace_layout.addWidget(replace_label)
    replace_layout.addWidget(replace_input)
    layout.addLayout(replace_layout)

    # Buttons
    btn_layout = QHBoxLayout()
    btn_prev = QPushButton(tr("Previous"))
    btn_next = QPushButton(tr("Next"))
    btn_replace = QPushButton(tr("Replace"))
    btn_replace_all = QPushButton(tr("Replace All"))
    
    btn_layout.addWidget(btn_prev)
    btn_layout.addWidget(btn_next)
    btn_layout.addWidget(btn_replace)
    btn_layout.addWidget(btn_replace_all)
    layout.addLayout(btn_layout)

    # Store references
    main_window._find_dialog = dialog
    main_window._find_input = find_input
    main_window._replace_input = replace_input

    # Connect signals
    btn_next.clicked.connect(lambda: _find_next(main_window))
    btn_prev.clicked.connect(lambda: _find_prev(main_window))
    find_input.returnPressed.connect(lambda: _find_next(main_window))
    btn_replace.clicked.connect(lambda: _replace_current(main_window))
    btn_replace_all.clicked.connect(lambda: _replace_all(main_window))

    dialog.show()
    find_input.setFocus()


def _find_next(main_window):
    if not hasattr(main_window, '_find_input') or main_window._find_input is None:
        _show_find_dialog(main_window)
        return
    text = main_window._find_input.text()
    if not text:
        return
    editor = _active_editor(main_window)
    from PyQt6.QtGui import QTextDocument
    found = editor.find(text)
    if not found:
        # Wrap around to the beginning
        cursor = editor.textCursor()
        cursor.movePosition(cursor.MoveOperation.Start)
        editor.setTextCursor(cursor)
        editor.find(text)


def _find_prev(main_window):
    if not hasattr(main_window, '_find_input') or main_window._find_input is None:
        return
    text = main_window._find_input.text()
    if not text:
        return
    editor = _active_editor(main_window)
    from PyQt6.QtGui import QTextDocument
    found = editor.find(text, QTextDocument.FindFlag.FindBackward)
    if not found:
        cursor = editor.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        editor.setTextCursor(cursor)
        editor.find(text, QTextDocument.FindFlag.FindBackward)


def _replace_current(main_window):
    if not hasattr(main_window, '_find_input'):
        return
    editor = _active_editor(main_window)
    cursor = editor.textCursor()
    if cursor.hasSelection() and cursor.selectedText() == main_window._find_input.text():
        cursor.insertText(main_window._replace_input.text())
    _find_next(main_window)


def _replace_all(main_window):
    if not hasattr(main_window, '_find_input'):
        return
    editor = _active_editor(main_window)
    find_text = main_window._find_input.text()
    replace_text = main_window._replace_input.text()
    if not find_text:
        return
    content = editor.toPlainText()
    new_content = content.replace(find_text, replace_text)
    if new_content != content:
        editor.setPlainText(new_content)


def _open_url(url):
    """Open a URL in the system's default web browser."""
    import webbrowser
    webbrowser.open(url)


def _show_about_dialog(main_window):
    """Show the About dialog with app info, icon, and library list."""
    import os
    from PyQt6.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QLabel
    from PyQt6.QtGui import QPixmap
    from PyQt6.QtCore import Qt
    from PyQt6.QtSvg import QSvgRenderer
    from PyQt6.QtGui import QPainter, QImage

    dialog = QDialog(main_window)
    dialog.setWindowTitle(tr("About zTikz"))
    dialog.setFixedSize(480, 340)

    main_layout = QHBoxLayout(dialog)

    # Left side: app icon
    icon_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', 'app_icon.svg')
    icon_label = QLabel()
    icon_label.setFixedSize(128, 128)
    icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    if os.path.exists(icon_path):
        renderer = QSvgRenderer(icon_path)
        image = QImage(128, 128, QImage.Format.Format_ARGB32)
        image.fill(0)
        painter = QPainter(image)
        renderer.render(painter)
        painter.end()
        pixmap = QPixmap.fromImage(image)
        icon_label.setPixmap(pixmap)
    main_layout.addWidget(icon_label, 0, Qt.AlignmentFlag.AlignTop)

    # Right side: text info
    info_layout = QVBoxLayout()

    title_label = QLabel("<h2>zTikz Editor</h2>")
    info_layout.addWidget(title_label)

    version_label = QLabel(f"<b>{tr('Version:')}</b> 1.0")
    info_layout.addWidget(version_label)

    author_label = QLabel(f"<b>{tr('Author:')}</b> Paulo Loma Marconi")
    info_layout.addWidget(author_label)

    website_label = QLabel(f'<b>{tr("Website:")}</b> <a href="https://paulomarconi.github.io">paulomarconi.github.io</a>')
    website_label.setOpenExternalLinks(True)
    info_layout.addWidget(website_label)

    libs_label = QLabel(
        f"<br><b>{tr('Key Libraries:')}</b>"
        "<ul>"
        f"<li>PyQt6 — {tr('GUI framework')}</li>"
        f"<li>ANTLR4 — {tr('TikZ code parsing')}</li>"
        f"<li>pdflatex — {tr('LaTeX compilation')}</li>"
        f"<li>PyMuPDF — {tr('PDF to PNG rendering')}</li>"
        f"<li>Python 3 — {tr('Runtime')}</li>"
        "</ul>"
    )
    libs_label.setWordWrap(True)
    info_layout.addWidget(libs_label)

    info_layout.addStretch()
    main_layout.addLayout(info_layout)

    dialog.exec()


def _show_settings_dialog(main_window):
    """Show the Settings dialog with General options."""
    from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                 QLineEdit, QPushButton, QGroupBox, QCheckBox,
                                 QComboBox, QMessageBox)
    from PyQt6.QtCore import Qt
    from zTikz.utils.latex import (find_pdflatex, executable_file_filter,
                                   pdflatex_placeholder, pdf_viewer_placeholder)

    dialog = QDialog(main_window)
    dialog.setWindowTitle(tr("Settings"))
    dialog.setMinimumWidth(700)  # <-- Change this value to adjust the window width

    layout = QVBoxLayout(dialog)

    # ── General group ──
    general_group = QGroupBox(tr("General"))
    general_layout = QVBoxLayout(general_group)

    # --- pdfLaTeX path ---
    path_label = QLabel(f"<b>{tr('Path to pdfLaTeX:')}</b>")
    general_layout.addWidget(path_label)

    path_row = QHBoxLayout()
    latex_input = QLineEdit()

    default_latex = find_pdflatex() or ""      # what auto-detection finds (PATH, then usual TeX folders)
    current_latex = getattr(main_window, '_pdflatex_path', None) or default_latex
    latex_input.setText(current_latex)
    latex_input.setPlaceholderText(pdflatex_placeholder())

    latex_browse = QPushButton(tr("Browse..."))
    latex_reset = QPushButton(tr("Reset Default"))

    def browse_latex():
        from PyQt6.QtWidgets import QFileDialog
        fp, _ = QFileDialog.getOpenFileName(
            dialog, "Select pdfLaTeX executable", "",
            executable_file_filter()
        )
        if fp:
            latex_input.setText(fp)

    latex_browse.clicked.connect(browse_latex)
    latex_reset.clicked.connect(lambda: latex_input.setText(default_latex))

    path_row.addWidget(latex_input)
    path_row.addWidget(latex_browse)
    path_row.addWidget(latex_reset)
    general_layout.addLayout(path_row)

    # --- External PDF viewer path ---
    pdf_label = QLabel(f"<b>{tr('Path to external PDF viewer:')}</b>")
    general_layout.addWidget(pdf_label)

    pdf_row = QHBoxLayout()
    pdf_input = QLineEdit()

    # Empty means "use the system's default PDF viewer" (works the same on every OS)
    default_pdf = ""
    pdf_input.setText(getattr(main_window, '_pdf_viewer_path', None) or default_pdf)
    pdf_input.setPlaceholderText(f"{tr('Empty = system default viewer')}  ({pdf_viewer_placeholder()})")

    pdf_browse = QPushButton(tr("Browse..."))
    pdf_reset = QPushButton(tr("Reset Default"))

    def browse_pdf():
        from PyQt6.QtWidgets import QFileDialog
        fp, _ = QFileDialog.getOpenFileName(
            dialog, "Select PDF viewer executable", "",
            executable_file_filter()
        )
        if fp:
            pdf_input.setText(fp)

    pdf_browse.clicked.connect(browse_pdf)
    pdf_reset.clicked.connect(lambda: pdf_input.setText(default_pdf))

    pdf_row.addWidget(pdf_input)
    pdf_row.addWidget(pdf_browse)
    pdf_row.addWidget(pdf_reset)
    general_layout.addLayout(pdf_row)

    # --- Check for updates on startup ---
    check_updates_cb = QCheckBox(tr("Check for updates on startup"))
    check_updates_cb.setChecked(getattr(main_window, '_check_updates_on_startup', False))
    general_layout.addWidget(check_updates_cb)

    # --- Language selection ---
    lang_row = QHBoxLayout()
    lang_label = QLabel(f"<b>{tr('Language:')}</b>")
    lang_combo = QComboBox()
    lang_combo.addItems(["English", "Español"])
    current_lang = getattr(main_window, '_language', 'English')
    lang_combo.setCurrentText(current_lang)
    lang_row.addWidget(lang_label)
    lang_row.addWidget(lang_combo)
    lang_row.addStretch()
    general_layout.addLayout(lang_row)

    layout.addWidget(general_group)

    # ── OK / Cancel buttons ──
    btn_row = QHBoxLayout()
    btn_row.addStretch()
    ok_btn = QPushButton(tr("OK"))
    cancel_btn = QPushButton(tr("Cancel"))

    def apply_settings():
        # Keep an override only if it differs from what auto-detection finds, so a moved or
        # upgraded TeX installation is picked up without visiting Settings again.
        latex_path = latex_input.text().strip()
        if latex_path == default_latex:
            latex_path = ""
        latex_changed = (latex_path or None) != getattr(main_window, '_pdflatex_path', None)
        main_window._pdflatex_path = latex_path or None
        main_window.settings.setValue('pdflatex_path', latex_path)

        pdf_path = pdf_input.text().strip()
        main_window._pdf_viewer_path = pdf_path or None
        main_window.settings.setValue('pdf_viewer_path', pdf_path)

        if latex_changed:
            # A different pdflatex can't reuse the old precompiled format; start afresh.
            main_window._fmt_static_hash = None
            main_window._fmt_failed_hash = None
            main_window._pdflatex_missing_reported = None
            main_window._last_compiled_hash = ''
            main_window.compile_tikz()

        main_window._check_updates_on_startup = check_updates_cb.isChecked()

        selected_lang = lang_combo.currentText()
        main_window._language = selected_lang
        set_language(selected_lang)

        # Rebuild the menu bar with the new language
        new_menu_bar = create_menu(main_window)
        main_window.setMenuBar(new_menu_bar)
        
        # Update existing widgets (tabs, tooltips, etc.)
        if hasattr(main_window, 'retranslateUi'):
            main_window.retranslateUi()

        dialog.accept()

    ok_btn.clicked.connect(apply_settings)
    cancel_btn.clicked.connect(dialog.reject)
    btn_row.addWidget(ok_btn)
    btn_row.addWidget(cancel_btn)
    layout.addLayout(btn_row)

    dialog.exec()