# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path
from PyInstaller.utils.hooks import Tree

block_cipher = None
base_dir = Path(__file__).parent

a = Analysis(
    ['app.pyw'],
    pathex=[],
    binaries=[],
    datas=[
        # sertakan seluruh folder config
        (Tree(str(base_dir / 'config'), prefix='config')),
        # sertakan templates
        (Tree(str(base_dir / 'templates'), prefix='templates')),
        # sertakan static
        (Tree(str(base_dir / 'static'), prefix='static')),
        # sertakan database
        (str(base_dir / 'fajarmandiri.db'), '.'),
        # icon
        (str(base_dir / 'icon.ico'), '.'),
        # cloudflared binary (Windows/Linux)
        (str(base_dir / 'cloudflared.exe'), '.'),  # Windows
        (str(base_dir / 'cloudflared'), '.'),      # Linux
    ],
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
    console=False,  # False = tidak ada jendela console
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
