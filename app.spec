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

# Update Windows spec file untuk include cloudflare_tunnel
# Hidden imports for Windows
hidden_imports = [
    'flask',
    'flask_socketio',
    'eventlet',
    'socketio',
    'engineio',
    'werkzeug',
    'werkzeug.serving',
    'jinja2',
    'markupsafe',
    'itsdangerous',
    'click',
    'blinker',
    'threading',
    'queue',
    'select',
    'socket',
    'ssl',
    'time',
    'datetime',
    'sqlite3',
    'os',
    'sys',
    'json',
    'uuid',
    'base64',
    'io',
    'PIL',
    'PIL.Image',
    'PIL.ImageDraw',
    'qrcode',
    'selenium',
    'selenium.webdriver',
    'selenium.webdriver.chrome.options',
    'selenium.webdriver.common.by',
    'selenium.webdriver.support.ui',
    'selenium.webdriver.support.expected_conditions',
    'webdriver_manager',
    'webdriver_manager.chrome',
    'google_auth_oauthlib',
    'google_auth_oauthlib.flow',
    'google.auth.transport.requests',
    'google.oauth2.credentials',
    'googleapiclient.discovery',
    'pystray',
    'psutil',
    'cloudflare_tunnel',
    'subprocess',
    'pathlib',
    'platform',
    'signal',
    'shutil'
]

# Update Windows spec file untuk include cloudflare_tunnel
# Data files
datas = [
    ('templates', 'templates'),
    ('static', 'static'),
    ('fajarmandiri.db', '.'),
    ('icon.ico', '.'),
    ('favicon.ico', '.'),
    ('cloudflare_tunnel.py', '.'),
    ('attached_assets', 'attached_assets'),
]