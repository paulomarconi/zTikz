# -*- mode: python ; coding: utf-8 -*-
import sys

block_cipher = None

datas = [
    ('zTikz/resources/*.json', 'zTikz/resources'),
    ('zTikz/resources/*.txt', 'zTikz/resources'),
    ('zTikz/resources/*.tex', 'zTikz/resources'),
    ('zTikz/resources/icons/*', 'zTikz/resources/icons'),
    ('zTikz/resources/snippets_icons/*', 'zTikz/resources/snippets_icons'),
    ('zTikz/antlr/*.g4', 'zTikz/antlr'),
    ('zTikz/antlr/*.interp', 'zTikz/antlr'),
    ('zTikz/antlr/*.tokens', 'zTikz/antlr'),
]

a = Analysis(
    ['zTikz_run.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'PyQt6.QtCore', 
        'PyQt6.QtGui', 
        'PyQt6.QtWidgets', 
        'fitz', 
        'antlr4'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['hide_console_hook.py'],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='zTikz',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=(sys.platform == 'darwin'),
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='zTikz.app',
        icon=None,
        bundle_identifier='com.paulomarconi.ztikz',
    )
