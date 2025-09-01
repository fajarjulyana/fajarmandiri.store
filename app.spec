
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Hidden imports untuk SocketIO dan dependencies
hidden_imports = [
    'eventlet',
    'eventlet.wsgi',
    'eventlet.green',
    'eventlet.hubs',
    'eventlet.hubs.epolls',
    'eventlet.hubs.kqueue', 
    'eventlet.hubs.selects',
    'eventlet.green.threading',
    'eventlet.green.socket',
    'socketio',
    'socketio.server',
    'socketio.client',
    'engineio',
    'engineio.server',
    'engineio.client',
    'engineio.async_drivers.threading',
    'engineio.async_drivers.eventlet',
    'flask_socketio',
    'threading',
    'queue',
    'select',
    'ssl',
    'urllib3',
    'werkzeug',
    'werkzeug.serving',
    'jinja2',
    'markupsafe',
    'flask',
    'itsdangerous',
    'click',
    'blinker',
    'dns',
    'dns.resolver',
    'six',
    'greenlet'
]

# Data files yang perlu disertakan
datas = [
    ('templates', 'templates'),
    ('static', 'static'),
    ('fajarmandiri.db', '.'),
    ('icon.ico', '.')
]

a = Analysis(
    ['app.pyw'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'
)
