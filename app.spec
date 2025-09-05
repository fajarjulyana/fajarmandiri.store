
# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for FajarMandiri Store v1.8.0
# Build: pyinstaller app.spec

import sys
import os

block_cipher = None

# Hidden imports untuk SocketIO dan dependencies v1.8.0
hidden_imports = [
    # Flask dan core dependencies
    'flask',
    'flask_socketio',
    'werkzeug',
    'werkzeug.serving',
    'jinja2',
    'markupsafe',
    'itsdangerous',
    'click',
    'blinker',
    
    # SocketIO dan real-time chat
    'socketio',
    'socketio.server',
    'socketio.client',
    'engineio',
    'engineio.server', 
    'engineio.client',
    'engineio.async_drivers.threading',
    'engineio.async_drivers.eventlet',
    
    # Eventlet untuk async
    'eventlet',
    'eventlet.wsgi',
    'eventlet.green',
    'eventlet.hubs',
    'eventlet.hubs.epolls',
    'eventlet.hubs.kqueue',
    'eventlet.hubs.selects',
    'eventlet.green.threading',
    'eventlet.green.socket',
    
    # System tray dan desktop integration
    'pystray',
    'pystray._win32',
    'pystray._base',
    'PIL',
    'PIL.Image',
    'PIL.ImageDraw',
    'PIL.ImageFont',
    
    # Database dan storage
    'sqlite3',
    'psutil',
    
    # Networking dan security
    'threading',
    'queue',
    'select',
    'ssl',
    'urllib3',
    'dns',
    'dns.resolver',
    'six',
    'greenlet',
    
    # Authentication (Google OAuth)
    'google',
    'google.auth',
    'google.oauth2',
    'oauthlib',
    'requests_oauthlib',
    
    # QR Code generation
    'qrcode',
    'qrcode.image',
    'qrcode.image.pil',
    
    # Image processing
    'selenium',
    'selenium.webdriver',
    'selenium.webdriver.chrome',
    'selenium.webdriver.common',
    
    # Additional utilities
    'subprocess',
    'shutil',
    'os',
    'sys',
    'json',
    'datetime',
    'time'
]

# Data files yang perlu disertakan v1.7.5
datas = [
    ('templates', 'templates'),
    ('static', 'static'),
    ('fajarmandiri.db', '.'),
    ('icon.ico', '.'),
    ('config', 'config'),
    ('cloudflared.exe', '.'),
    # Include Documents folder structure for template storage
    ('README.md', '.'),
    ('requirements.txt', '.')
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
    name='FajarMandiriStore-v1.7.5',
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
    icon='icon.ico',
    version_info={
        'version': '1.7.5.0',
        'description': 'FajarMandiri Store - Wedding Invitation & CV Generator',
        'company': 'Fajar Mandiri Store',
        'product': 'FajarMandiri Store',
        'copyright': '© 2025 Fajar Julyana - Fajar Mandiri Store'
    }
)
