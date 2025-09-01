# -*- mode: python ; coding: utf-8 -*-

import sys
import os, glob
from pathlib import Path

block_cipher = None
base_dir = Path(".").resolve()

def collect_folder(folder, target):
    files = []
    folder_path = os.path.join(base_dir, folder)
    if os.path.exists(folder_path):
        for f in glob.glob(os.path.join(folder_path, '**'), recursive=True):
            if os.path.isfile(f):
                files.append((f, os.path.join(target, os.path.relpath(f, folder_path))))
    return files

datas = []
datas += collect_folder('config', 'config')
datas += collect_folder('templates', 'templates')
datas += collect_folder('static', 'static')
datas += [(str(base_dir / 'fajarmandiri.db'), '.')]
datas += [(str(base_dir / 'icon.ico'), '.')]
datas += [(str(base_dir / 'cloudflared.exe'), '.')]
datas += [(str(base_dir / 'cloudflared'), '.')]

a = Analysis(
    ['app.pyw'],   # ganti ke app.pyw kalau perlu
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "engineio.async_drivers.threading",
        "socketio.asyncio_namespace",
        "socketio.asyncio_server",
        "socketio.asyncio_client",
        "socketio.asyncio_manager",
        "socketio.asyncio_pubsub_manager",
        "socketio.asyncio_redis_manager",
        "socketio.asyncio_aioredis_manager",
        "socketio.asyncio_kafka_manager",
        "socketio.asyncio_zmq_manager",
        "eventlet",
        "gevent",
        "gevent.monkey",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
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
    [],
    exclude_binaries=True,
    name='FajarMandiriService',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # False = tanpa console
    icon=str(base_dir / 'icon.ico'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FajarMandiriService'
)

app = BUNDLE(
    coll,
    name='FajarMandiriService.exe',
    icon=str(base_dir / 'icon.ico'),
    bundle_identifier=None
)
