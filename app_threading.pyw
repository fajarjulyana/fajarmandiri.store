
from flask import Flask, render_template, render_template_string, request, redirect, url_for, flash, session, send_file, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import sqlite3
import os
import json
import uuid
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import google_auth_oauthlib.flow
import google.auth.transport.requests
import google.oauth2.credentials
from googleapiclient.discovery import build
import qrcode
from io import BytesIO
import base64
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import time
from datetime import datetime
from PIL import Image

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Path universal ke Documents user
USER_DOCS = os.path.join(os.path.expanduser("~"), "Documents", "FajarMandiriStore")

# SocketIO dengan threading mode saja (lebih kompatibel dengan PyInstaller)
print("Initializing SocketIO with threading mode for PyInstaller compatibility...")
try:
    socketio = SocketIO(
        app, 
        cors_allowed_origins="*", 
        async_mode="threading",
        logger=False,
        engineio_logger=False,
        ping_timeout=60,
        ping_interval=25
    )
    print("SocketIO initialized successfully with threading mode")
except Exception as e:
    print(f"Failed to initialize SocketIO: {str(e)}")
    # Create minimal dummy for basic functionality
    class MinimalSocketIO:
        def run(self, *args, **kwargs):
            print("Running Flask without SocketIO...")
            app.run(*args, **kwargs)
        def emit(self, *args, **kwargs):
            print("SocketIO emit called (dummy)")
        def on(self, event):
            def decorator(f):
                print(f"SocketIO event handler registered (dummy): {event}")
                return f
            return decorator
    socketio = MinimalSocketIO()

# Konfigurasi folder
app.config['UPLOAD_FOLDER'] = USER_DOCS
app.config['TEMPLATES_FOLDER'] = 'cv_templates'
app.config['WEDDING_FOLDER'] = 'wedding_templates'
app.config['MUSIC_FOLDER'] = os.path.join(USER_DOCS, "music")
app.config['PREWEDDING_FOLDER'] = os.path.join(USER_DOCS, "prewedding_photos")

# Create necessary directories
for folder in [app.config['UPLOAD_FOLDER'], app.config['TEMPLATES_FOLDER'],
               app.config['WEDDING_FOLDER'], app.config['MUSIC_FOLDER'],
               app.config['PREWEDDING_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

# Sisanya sama dengan app.pyw yang asli...
# [Copy semua fungsi dan routes dari app.pyw di sini]

# Import semua fungsi dari app.pyw
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Load konfigurasi dari app.pyw
exec(open('app.pyw').read().split('if __name__ == "__main__":')[0])

# Override socketio.run untuk lebih stabil
def run_flask():
    try:
        from app import init_db
        init_db()

        # Buka browser otomatis setelah delay kecil
        def open_browser():
            time.sleep(3)
            url = "http://localhost:5001"
            import webbrowser
            import platform
            import subprocess
            
            if platform.system() == "Windows":
                try:
                    subprocess.Popen(
                        ["cmd", "/c", "start chrome --kiosk " + url],
                        shell=True
                    )
                except Exception:
                    webbrowser.open(url)
            else:
                webbrowser.open(url)

        import threading
        threading.Thread(target=open_browser, daemon=True).start()

        # Run dengan error handling yang lebih baik
        try:
            if hasattr(socketio, 'run') and callable(socketio.run):
                print("Starting server with SocketIO...")
                socketio.run(
                    app,
                    host="0.0.0.0",
                    port=5001,
                    debug=False,
                    use_reloader=False,
                    allow_unsafe_werkzeug=True
                )
            else:
                print("Starting server with Flask only...")
                app.run(
                    host="0.0.0.0",
                    port=5001,
                    debug=False,
                    use_reloader=False
                )
        except Exception as e:
            print(f"Server failed to start: {str(e)}")
            print("Trying basic Flask server...")
            app.run(host="0.0.0.0", port=5001, debug=False)

    except Exception as e:
        print(f"Critical error in run_flask: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import sys
    import time
    import threading
    import subprocess
    import webbrowser
    import traceback
    import platform
    import socket

    from pystray import Icon, Menu, MenuItem
    from PIL import Image, ImageDraw
    import psutil

    # Jalankan service
    def start_service(icon=None, item=None):
        global server_thread
        server_thread = threading.Thread(target=run_flask, daemon=True)
        server_thread.start()

    def stop_service(icon=None, item=None):
        try:
            if icon:
                icon.stop()
        except:
            pass

        # Kill child processes
        parent = psutil.Process(os.getpid())
        for child in parent.children(recursive=True):
            try:
                child.kill()
            except:
                pass

        os._exit(0)

    # Tray icon
    def get_tray_icon():
        try:
            base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
            icon_path = os.path.join(base_path, "icon.ico")

            if os.path.exists(icon_path):
                return Image.open(icon_path)
            else:
                # fallback
                image = Image.new("RGB", (64, 64), (0, 0, 0, 0))
                dc = ImageDraw.Draw(image)
                dc.ellipse((8, 8, 56, 56), fill="blue")
                return image
        except Exception as e:
            # fallback
            image = Image.new("RGB", (64, 64), (0, 0, 0, 0))
            dc = ImageDraw.Draw(image)
            dc.ellipse((8, 8, 56, 56), fill="blue")
            return image

    menu = Menu(
        MenuItem("Start Service", start_service),
        MenuItem("Stop Service", stop_service),
    )

    def run_tray():
        try:
            icon = Icon("Fajar Mandiri Service", get_tray_icon(), menu=menu)
            icon.run()
        except Exception as e:
            print(f"Tray error: {str(e)}")

    start_service()
    threading.Thread(target=run_tray, daemon=True).start()

    # Loop biar process tetap hidup
    while True:
        time.sleep(1)
