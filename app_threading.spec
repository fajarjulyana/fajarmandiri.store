
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Minimal hidden imports yang benar-benar diperlukan
hidden_imports = [
    'flask',
    'flask_socketio',
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
    'psutil'
]

# Data files
datas = [
    ('templates', 'templates'),
    ('static', 'static'),
    ('fajarmandiri.db', '.'),
    ('icon.ico', '.')
]

a = Analysis(
    ['app_threading.pyw'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['eventlet'],  # Exclude eventlet to force threading mode
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
    name='FajarMandiriStore',
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
