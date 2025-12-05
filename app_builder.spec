# -*- mode: python ; coding: utf-8 -*-
import os
os.environ["SKLEARN_SKIP_HTML"] = "1"

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

hiddenimports = collect_submodules('sklearn')
datas = collect_data_files('sklearn')

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/model.pkl', 'assets'),
        ('assets/logs.log', 'assets'),
        ('assets/favicon.ico', 'assets'),
        *datas
    ],
    hiddenimports=hiddenimports,
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
    [],
    exclude_binaries=True,
    name='YoutubeCommentsRemover(BETA)',
    debug=False,
    upx=True,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name='YoutubeCommentsRemover(BETA)',
)