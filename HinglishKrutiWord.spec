# -*- mode: python ; coding: utf-8 -*-
# Lean PyQt6 bundle: widgets-only app — avoids huge QML payload and flaky onefile+UPX on Windows.

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
hiddenimports=['hinlang', 'PyQt6.QtPrintSupport', 'docx', 'python-docx'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='HinglishKrutiWord',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
