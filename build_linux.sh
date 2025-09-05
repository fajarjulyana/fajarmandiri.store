
#!/bin/bash

echo "Building FajarMandiri Store for Linux..."

# Set colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    print_error "This script is designed to run on Linux"
    exit 1
fi

# Check dependencies
print_status "Checking dependencies..."
python3 check_dependencies.py
if [ $? -ne 0 ]; then
    print_warning "Installing missing dependencies..."
    pip3 install -r requirements.txt
    
    # Check again
    python3 check_dependencies.py
    if [ $? -ne 0 ]; then
        print_error "Some dependencies are still missing. Please check manually."
        exit 1
    fi
fi

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    print_status "Installing PyInstaller..."
    pip3 install pyinstaller
fi

# Clean previous builds
print_status "Cleaning previous builds..."
if [ -d "build" ]; then
    rm -rf build
fi
if [ -d "dist" ]; then
    rm -rf dist
fi

# Copy templates to Documents for packaged application
print_status "Setting up templates for Documents folder..."
python3 copy_templates_to_documents.py

# Create Linux-specific spec file
print_status "Creating Linux-specific spec file..."
cat > app_linux.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Hidden imports untuk Linux
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
    'psutil',
    'cloudflare_tunnel',
    'subprocess',
    'pathlib',
    'platform',
    'signal',
    'shutil'
]

# Data files - minimal for /opt installation
datas = [
    ('templates', 'templates'),
    ('static', 'static'),
    ('fajarmandiri.db', '.'),
    ('cloudflare_tunnel.py', '.'),
    ('copy_templates_to_documents.py', '.'),
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
    name='fajarmandiri-store',
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
)
EOF

# Build with PyInstaller
print_status "Building with PyInstaller..."
pyinstaller app_linux.spec

if [ $? -eq 0 ]; then
    print_status "Build completed successfully!"
    print_status "Executable location: dist/fajarmandiri-store"
    
    # Test the executable
    if [ -f "dist/fajarmandiri-store" ]; then
        print_status "✓ Executable created successfully"
        ls -la dist/fajarmandiri-store
        chmod +x dist/fajarmandiri-store
    else
        print_error "✗ Executable not found"
        exit 1
    fi
else
    print_error "Build failed!"
    exit 1
fi

print_status "Linux build completed successfully!"
