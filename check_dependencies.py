
"""
Script untuk mengecek dependencies yang diperlukan sebelum build
"""
import sys
import importlib

required_packages = [
    'flask',
    'flask_socketio', 
    'eventlet',
    'socketio',
    'engineio',
    'werkzeug',
    'jinja2',
    'markupsafe',
    'itsdangerous',
    'click',
    'blinker',
    'selenium',
    'webdriver_manager',
    'pillow',
    'qrcode',
    'google_auth_oauthlib',
    'google_api_python_client',
    'pystray',
    'psutil'
]

def check_package(package_name):
    try:
        importlib.import_module(package_name)
        print(f" {package_name}")
        return True
    except ImportError:
        print(f" {package_name} - MISSING")
        return False

def main():
    print("Checking required packages for PyInstaller build...")
    print("=" * 50)
    
    missing_packages = []
    
    for package in required_packages:
        if not check_package(package):
            missing_packages.append(package)
    
    print("=" * 50)
    
    if missing_packages:
        print(f"Missing packages: {', '.join(missing_packages)}")
        print("Please install missing packages before building.")
        return False
    else:
        print("All required packages are available!")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
