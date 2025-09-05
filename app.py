from flask import Flask, render_template, render_template_string, request, redirect, url_for, flash, session, send_file, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import sqlite3
import os
import json
import uuid
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import time
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
app.secret_key = os.environ.get('FLASK_SECRET_KEY',
                                'dev-secret-key-change-in-production')
# Path universal ke Documents user
USER_DOCS = os.path.join(os.path.expanduser("~"), "Documents",
                         "FajarMandiriStore")

# ============================
# Midtrans Configuration
# ============================
import os
from dotenv import load_dotenv

# Load .env file (jika ada)
load_dotenv()

MIDTRANS_MERCHANT_ID  = os.getenv("MIDTRANS_MERCHANT_ID")
MIDTRANS_CLIENT_KEY   = os.getenv("MIDTRANS_CLIENT_KEY")
MIDTRANS_SERVER_KEY   = os.getenv("MIDTRANS_SERVER_KEY")

# Set default values for development if not provided
if not MIDTRANS_MERCHANT_ID:
    MIDTRANS_MERCHANT_ID = "G000000000"
    print("⚠️  Using default Midtrans Merchant ID for development")

if not MIDTRANS_CLIENT_KEY:
    MIDTRANS_CLIENT_KEY = "SB-Mid-client-dev"
    print("⚠️  Using default Midtrans Client Key for development")

if not MIDTRANS_SERVER_KEY:
    MIDTRANS_SERVER_KEY = "SB-Mid-server-dev"
    print("⚠️  Using default Midtrans Server Key for development")

# Debug (nonaktifkan di production)
print("DEBUG Midtrans Config:")
print("  Merchant ID :", MIDTRANS_MERCHANT_ID)
print("  Client Key  :", (MIDTRANS_CLIENT_KEY[:10] + "...") if len(MIDTRANS_CLIENT_KEY) > 10 else MIDTRANS_CLIENT_KEY)
print("  Server Key  :", (MIDTRANS_SERVER_KEY[:10] + "...") if len(MIDTRANS_SERVER_KEY) > 10 else MIDTRANS_SERVER_KEY)

# Penting: hanya ada baris ini untuk socketio
# Fix untuk PyInstaller - coba berbagai async_mode secara bertahap
def create_socketio():
    """Create SocketIO instance with fallback modes for PyInstaller compatibility"""
    modes_to_try = ['threading', 'eventlet', None]

    for mode in modes_to_try:
        try:
            if mode is None:
                print(f"Trying SocketIO without async_mode (auto-detect)")
                return SocketIO(app,
                                cors_allowed_origins="*",
                                logger=False,
                                engineio_logger=False)
            else:
                print(f"Trying SocketIO with async_mode: {mode}")
                return SocketIO(app,
                                cors_allowed_origins="*",
                                async_mode=mode,
                                logger=False,
                                engineio_logger=False)
        except Exception as e:
            print(
                f"Failed to create SocketIO with async_mode={mode}: {str(e)}")
            continue

    # Ultimate fallback - basic SocketIO without any special config
    print("Using basic SocketIO configuration as final fallback")
    return SocketIO(app,
                    cors_allowed_origins="*",
                    logger=False,
                    engineio_logger=False)


try:
    socketio = create_socketio()
    print("SocketIO initialized successfully")
except Exception as e:
    print(f"Critical error initializing SocketIO: {str(e)}")

    # Create a dummy socketio object that won't crash the app
    class DummySocketIO:

        def run(self, *args, **kwargs):
            print("Running Flask without SocketIO due to initialization error")
            app.run(*args, **kwargs)

        def emit(self, *args, **kwargs):
            pass

        def on(self, *args, **kwargs):

            def decorator(f):
                return f

            return decorator

    socketio = DummySocketIO()
app.config['UPLOAD_FOLDER'] = USER_DOCS
app.config['TEMPLATES_FOLDER'] = os.path.join(USER_DOCS, 'cv_templates')
app.config['WEDDING_FOLDER'] = os.path.join(USER_DOCS, 'wedding_templates')
app.config['MUSIC_FOLDER'] = os.path.join(USER_DOCS, "music")
app.config['PREWEDDING_FOLDER'] = os.path.join(USER_DOCS, "prewedding_photos")
app.config['THUMBNAILS_FOLDER'] = os.path.join(USER_DOCS, "thumbnails")
app.config['WEDDING_THUMBNAILS_FOLDER'] = os.path.join(USER_DOCS, "thumbnails",
                                                       "wedding_templates")
app.config['CV_THUMBNAILS_FOLDER'] = os.path.join(USER_DOCS, "thumbnails",
                                                  "cv_templates")

# Create necessary directories
for folder in [
        app.config['UPLOAD_FOLDER'], app.config['TEMPLATES_FOLDER'],
        app.config['WEDDING_FOLDER'], app.config['MUSIC_FOLDER'],
        app.config['PREWEDDING_FOLDER']
]:
    os.makedirs(folder, exist_ok=True)

# Google OAuth configuration
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')

oauth_config = {
    "web": {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token"
    }
}


def check_and_update_template_files():
    """Check and update template files in database"""
    try:
        conn = get_db()
        templates = conn.execute(
            'SELECT id, name, template_file FROM wedding_templates').fetchall()

        # Available template files
        template_files = [
            'black_luxury_gold.html', 'blue_luxury_gold.html',
            'red_luxury_gold.html', 'elegant_cream.html',
            'MandiriTheme_Style.html', 'MandiriTheme_Style_1.html',
            'MandiriTheme_Style_2.html', 'MandiriTheme_Style_3.html',
            'MandiriTheme_classic.html', 'MandiriTheme_elegant.html',
            'MandiriTheme_modern.html', 'classic_romance.html',
            'elegant_golden.html', 'garden_fresh.html', 'garden_romance.html',
            'luxury_modern.html', 'minimal_blush.html',
            'modern_minimalist.html', 'ocean_waves.html',
            'royal_burgundy.html', 'vintage_charm.html'
        ]

        updated_count = 0
        for i, template in enumerate(templates):
            if not template['template_file'] or template['template_file'] == '':
                # Assign template file based on index or name
                if i < len(template_files):
                    new_template_file = template_files[i]
                else:
                    # Use black_luxury_gold.html as default
                    new_template_file = 'black_luxury_gold.html'

                print(
                    f"Updating template {template['name']} (ID: {template['id']}) with file: {new_template_file}"
                )
                conn.execute(
                    'UPDATE wedding_templates SET template_file = ? WHERE id = ?',
                    (new_template_file, template['id']))
                updated_count += 1

        if updated_count > 0:
            conn.commit()
            print(
                f"Updated {updated_count} templates with missing template files"
            )
        else:
            print("All templates have template files assigned")

        # Verify all templates have valid template files
        print("All templates have valid template files")

        conn.close()

    except Exception as e:
        print(f"Error checking template files: {str(e)}")


def setup_default_templates():
    """Setup default templates if none exist"""
    try:
        conn = get_db()

        # Check wedding templates
        wedding_count = conn.execute('SELECT COUNT(*) FROM wedding_templates').fetchone()[0]
        if wedding_count == 0:
            print("Setting up default wedding templates...")
            default_wedding_templates = [
                ('Elegant Cream', 'Template undangan elegan dengan warna cream', 'Gratis', 'elegant_cream.html', 'cream', 0, 0),
                ('Black Luxury Gold', 'Template undangan mewah hitam emas', 'Premium', 'black_luxury_gold.html', 'elegant', 1, 35000),
                ('Blue Luxury Gold', 'Template undangan mewah biru emas', 'Premium', 'blue_luxury_gold.html', 'romantic', 1, 35000),
                ('Red Luxury Gold', 'Template undangan mewah merah emas', 'Premium', 'red_luxury_gold.html', 'classic', 1, 35000),
            ]

            for name, desc, category, file, color, premium, price in default_wedding_templates:
                conn.execute('''
                    INSERT INTO wedding_templates 
                    (name, description, category, template_file, color_scheme, is_premium, price)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (name, desc, category, file, color, premium, price))

            print(f"Added {len(default_wedding_templates)} default wedding templates")

        # Check CV templates
        cv_count = conn.execute('SELECT COUNT(*) FROM cv_templates').fetchone()[0]
        if cv_count == 0:
            print("Setting up default CV templates...")
            default_cv_templates = [
                ('Clean Professional', 'Template CV profesional bersih', 'professional', 'clean_professional.html', 'blue', 0),
                ('Modern Sidebar', 'Template CV modern dengan sidebar', 'modern', 'modern_sidebar.html', 'green', 1),
                ('Executive Dark', 'Template CV eksekutif gelap', 'executive', 'executive_dark.html', 'dark', 1),
                ('Timeline Professional', 'Template CV dengan timeline', 'creative', 'timeline_professional.html', 'purple', 1),
            ]

            for name, desc, category, file, color, premium in default_cv_templates:
                conn.execute('''
                    INSERT INTO cv_templates 
                    (name, description, category, template_file, color_scheme, is_premium)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (name, desc, category, file, color, premium))

            print(f"Added {len(default_cv_templates)} default CV templates")

        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Error setting up default templates: {str(e)}")


def reset_database():
    """Reset database dan buat ulang dengan struktur yang benar"""
    try:
        # Backup existing database
        if os.path.exists('fajarmandiri.db'):
            import shutil
            shutil.copy(
                'fajarmandiri.db',
                f'wedding_app_backup_{int(datetime.now().timestamp())}.db')

        # Hapus database lama
        if os.path.exists('fajarmandiri.db'):
            os.remove('fajarmandiri.db')

        print("Database lama dihapus, membuat database baru...")
        init_db()
        print("Database baru berhasil dibuat!")

    except Exception as e:
        print(f"Error reset database: {str(e)}")


DB_FILE = os.path.join(USER_DOCS, "fajarmandiri.db")


def init_db():
    """Initialize database with proper error handling and table checking"""
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10, check_same_thread=False)
        cursor = conn.cursor()

        # Check if core tables exist, if not create them
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='users'
        """)
        users_table_exists = cursor.fetchone()

        if not users_table_exists:
            print("Creating database tables...")

            # Users table
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                google_id TEXT,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                password TEXT,
                picture TEXT,
                is_premium BOOLEAN DEFAULT 0,
                is_banned BOOLEAN DEFAULT 0,
                is_blocked BOOLEAN DEFAULT 0,
                ban_reason TEXT,
                premium_expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')

            # Add missing columns if they don't exist
            try:
                cursor.execute('ALTER TABLE users ADD COLUMN ban_reason TEXT')
            except sqlite3.OperationalError:
                pass  # Column already exists
            try:
                cursor.execute('ALTER TABLE users ADD COLUMN current_plan TEXT DEFAULT "free"')
            except sqlite3.OperationalError:
                pass
            try:
                cursor.execute('ALTER TABLE users ADD COLUMN invitation_count INTEGER DEFAULT 0')
            except sqlite3.OperationalError:
                pass
            try:
                cursor.execute('ALTER TABLE users ADD COLUMN invitation_limit INTEGER DEFAULT 0')
            except sqlite3.OperationalError:
                pass
            try:
                cursor.execute('ALTER TABLE users ADD COLUMN cv_count INTEGER DEFAULT 0')
            except sqlite3.OperationalError:
                pass
            try:
                cursor.execute('ALTER TABLE users ADD COLUMN cv_limit INTEGER DEFAULT 0')
            except sqlite3.OperationalError:
                pass

            # Orders table
            cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                nama TEXT NOT NULL,
                email TEXT NOT NULL,
                whatsapp TEXT NOT NULL,
                jenis_cetakan TEXT NOT NULL,
                ukuran TEXT,
                jumlah INTEGER NOT NULL,
                warna TEXT,
                kertas TEXT,
                catatan TEXT,
                file_path TEXT,
                status TEXT DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )''')

            # CV templates table
            cursor.execute('''CREATE TABLE IF NOT EXISTS cv_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT,
                template_file TEXT NOT NULL,
                preview_image TEXT,
                is_premium BOOLEAN DEFAULT 0,
                color_scheme TEXT DEFAULT 'blue',
                animations TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')

            # Wedding templates table
            cursor.execute('''CREATE TABLE IF NOT EXISTS wedding_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT,
                template_file TEXT NOT NULL,
                preview_image TEXT,
                color_scheme TEXT DEFAULT 'elegant',
                animations TEXT DEFAULT '',
                background_music TEXT DEFAULT '',
                ornaments TEXT DEFAULT '',
                is_premium BOOLEAN DEFAULT 0,
                price INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')

            # Update existing templates with missing default values
            try:
                cursor.execute('UPDATE wedding_templates SET color_scheme = "elegant" WHERE color_scheme IS NULL')
                cursor.execute('UPDATE wedding_templates SET animations = "" WHERE animations IS NULL')
                cursor.execute('UPDATE wedding_templates SET ornaments = "" WHERE ornaments IS NULL')
                cursor.execute('UPDATE wedding_templates SET background_music = "" WHERE background_music IS NULL')
            except sqlite3.OperationalError:
                pass  # Columns might not exist yet

            # Wedding invitations table
            cursor.execute('''CREATE TABLE IF NOT EXISTS wedding_invitations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                couple_name TEXT NOT NULL,
                bride_name TEXT NOT NULL,
                bride_title TEXT DEFAULT '',
                bride_father TEXT NOT NULL,
                bride_mother TEXT NOT NULL,
                groom_name TEXT NOT NULL,
                groom_title TEXT DEFAULT '',
                groom_father TEXT NOT NULL,
                groom_mother TEXT NOT NULL,
                wedding_date DATE,
                wedding_time TEXT,
                venue_name TEXT,
                venue_address TEXT NOT NULL,
                template_id INTEGER NOT NULL DEFAULT 1,
                custom_message TEXT,
                invitation_link TEXT UNIQUE NOT NULL,
                qr_code TEXT,
                background_music TEXT,
                prewedding_photos TEXT,
                bank_name TEXT,
                bank_account TEXT,
                account_holder TEXT,
                qris_code TEXT,
                guest_limit INTEGER DEFAULT 100,
                is_active BOOLEAN DEFAULT 1,
                akad_date DATE,
                akad_time TEXT,
                akad_venue_name TEXT,
                akad_venue_address TEXT,
                resepsi_date DATE,
                resepsi_time TEXT,
                resepsi_venue_name TEXT,
                resepsi_venue_address TEXT,
                bride_event_date DATE,
                bride_event_time TEXT,
                bride_event_venue_name TEXT,
                bride_event_venue_address TEXT,
                groom_event_date DATE,
                groom_event_time TEXT,
                groom_event_venue_name TEXT,
                groom_event_venue_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (template_id) REFERENCES wedding_templates (id)
            )''')

            # Wedding guests table
            cursor.execute('''CREATE TABLE IF NOT EXISTS wedding_guests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invitation_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                attendance TEXT DEFAULT 'pending',
                guest_count INTEGER DEFAULT 1,
                message TEXT,
                wishes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (invitation_id) REFERENCES wedding_invitations (id)
            )''')

            # Ensure name column exists (it should, but let's be safe)
            try:
                cursor.execute('SELECT name FROM wedding_guests LIMIT 1')
            except sqlite3.OperationalError:
                cursor.execute('ALTER TABLE wedding_guests ADD COLUMN name TEXT NOT NULL DEFAULT ""')

            # Admin table
            cursor.execute('''CREATE TABLE IF NOT EXISTS admin (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            )''')

            # Premium subscriptions table
            cursor.execute('''CREATE TABLE IF NOT EXISTS premium_subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                payment_id INTEGER,
                subscription_type TEXT NOT NULL,
                plan_name TEXT NOT NULL DEFAULT 'basic',
                plan_price INTEGER NOT NULL DEFAULT 35000,
                invitation_limit INTEGER DEFAULT 2,
                cv_limit INTEGER DEFAULT -1,
                has_premium_templates BOOLEAN DEFAULT 1,
                start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_date TIMESTAMP NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )''')
            
            # Add new columns to existing premium_subscriptions table
            try:
                cursor.execute('ALTER TABLE premium_subscriptions ADD COLUMN plan_name TEXT DEFAULT "basic"')
            except sqlite3.OperationalError:
                pass  # Column already exists
            try:
                cursor.execute('ALTER TABLE premium_subscriptions ADD COLUMN plan_price INTEGER DEFAULT 35000')
            except sqlite3.OperationalError:
                pass  
            try:
                cursor.execute('ALTER TABLE premium_subscriptions ADD COLUMN invitation_limit INTEGER DEFAULT 2')
            except sqlite3.OperationalError:
                pass  
            try:
                cursor.execute('ALTER TABLE premium_subscriptions ADD COLUMN cv_limit INTEGER DEFAULT -1')
            except sqlite3.OperationalError:
                pass  
            try:
                cursor.execute('ALTER TABLE premium_subscriptions ADD COLUMN has_premium_templates BOOLEAN DEFAULT 1')
            except sqlite3.OperationalError:
                pass

            # Payments table
            cursor.execute('''CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                order_id TEXT UNIQUE NOT NULL,
                amount INTEGER NOT NULL,
                payment_type TEXT NOT NULL,
                payment_method TEXT,
                status TEXT DEFAULT 'pending',
                midtrans_transaction_id TEXT,
                payment_response TEXT,
                template_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )''')

            # Add template_id column if it doesn't exist
            try:
                cursor.execute('ALTER TABLE payments ADD COLUMN template_id INTEGER')
            except sqlite3.OperationalError:
                pass  # Column already exists

            # Chat messages table
            cursor.execute('''CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_type TEXT NOT NULL,
                sender_id INTEGER,
                sender_name TEXT NOT NULL,
                sender_email TEXT,
                message TEXT NOT NULL,
                room_type TEXT NOT NULL,
                room_id TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_read BOOLEAN DEFAULT 0
            )''')

            # Template access table for individual template purchases
            cursor.execute('''CREATE TABLE IF NOT EXISTS template_access (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                template_id INTEGER NOT NULL,
                template_type TEXT DEFAULT 'wedding',
                payment_id INTEGER,
                granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )''')

            # Insert default admin if not exists
            cursor.execute('SELECT COUNT(*) FROM admin WHERE username = ?', ('fajar',))
            if cursor.fetchone()[0] == 0:
                hashed_password = generate_password_hash('fajar123')
                cursor.execute('INSERT INTO admin (username, password) VALUES (?, ?)',
                              ('fajar', hashed_password))
                print("Admin default dibuat: username=fajar, password=fajar123")

            print("Database tables created successfully!")

        conn.commit()
        conn.close()
        print("Database initialization completed!")

        # Setup default templates if none exist
        try:
            setup_default_templates()
        except Exception as e:
            print(f"Warning: Template setup failed: {e}")

        # Update template files if needed
        try:
            check_and_update_template_files()
        except Exception as e:
            print(f"Warning: Template file check failed: {e}")

    except Exception as e:
        print(f" Database initialization error: {e}")
        # Don't re-raise the error to prevent application crash


def get_db():
    import sqlite3
    conn = sqlite3.connect(DB_FILE, timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


from flask import send_from_directory, abort
import os


@app.route('/documents/<path:filename>')
def uploaded_file(filename):
    # Path absolut ke folder "Documents/FajarMandiriStore"
    documents_dir = app.config['UPLOAD_FOLDER']

    # Pastikan file ada
    full_path = os.path.join(documents_dir, filename)
    if not os.path.isfile(full_path):
        abort(404)

    return send_from_directory(documents_dir, filename)


@app.route('/documents/music/<filename>')
def serve_documents_music(filename):
    """Serve music files from Documents/FajarMandiriStore/music folder"""
    music_dir = app.config['MUSIC_FOLDER']

    # Pastikan file ada
    full_path = os.path.join(music_dir, filename)
    if not os.path.isfile(full_path):
        abort(404)

    return send_from_directory(music_dir, filename)


@app.route('/documents/prewedding_photos/<filename>')
def serve_documents(filename):
    """Serve prewedding photos and other files from Documents/FajarMandiriStore"""
    prewedding_dir = app.config['PREWEDDING_FOLDER']

    # Pastikan file ada
    full_path = os.path.join(prewedding_dir, filename)
    if not os.path.isfile(full_path):
        abort(404)

    return send_from_directory(prewedding_dir, filename)


@app.route('/documents/wedding_templates/<filename>')
def serve_wedding_templates(filename):
    """Serve wedding template files from Documents/FajarMandiriStore/wedding_templates"""
    wedding_dir = app.config['WEDDING_FOLDER']

    # Pastikan file ada
    full_path = os.path.join(wedding_dir, filename)
    if not os.path.isfile(full_path):
        abort(404)

    return send_from_directory(wedding_dir, filename)


@app.route('/documents/thumbnails/wedding_templates/<filename>')
def serve_wedding_thumbnails(filename):
    """Serve wedding template thumbnails from Documents/FajarMandiriStore/thumbnails/wedding_templates"""
    thumbnails_dir = app.config['WEDDING_THUMBNAILS_FOLDER']

    # Pastikan file ada
    full_path = os.path.join(thumbnails_dir, filename)
    if not os.path.isfile(full_path):
        abort(404)

    return send_from_directory(thumbnails_dir, filename)


@app.route('/documents/thumbnails/cv_templates/<filename>')
def serve_cv_thumbnails(filename):
    """Serve CV template thumbnails from Documents/FajarMandiriStore/thumbnails/cv_templates"""
    thumbnails_dir = app.config['CV_THUMBNAILS_FOLDER']

    # Pastikan file ada
    full_path = os.path.join(thumbnails_dir, filename)
    if not os.path.isfile(full_path):
        abort(404)

    return send_from_directory(thumbnails_dir, filename)


# Authentication decorators
from functools import wraps

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu!', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def require_guest_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' in session:
            return redirect(url_for('dashboard'))
        if 'admin' in session:
            return redirect(url_for('admin_dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' not in session:
            flash('Akses ditolak! Silakan login sebagai admin.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
@require_guest_only
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE email = ?',
                            (email, )).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            session['user_picture'] = user['picture']
            session['is_premium'] = user['is_premium']

            flash(f'Selamat datang, {user["name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Email atau password salah!', 'error')

    return render_template('auth/login.html')


@app.route('/register', methods=['GET', 'POST'])
@require_guest_only
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Password konfirmasi tidak cocok!', 'error')
            return render_template('auth/register.html')

        if len(password) < 6:
            flash('Password minimal 6 karakter!', 'error')
            return render_template('auth/register.html')

        conn = get_db()
        existing_user = conn.execute('SELECT * FROM users WHERE email = ?',
                                     (email, )).fetchone()

        if existing_user:
            flash('Email sudah terdaftar!', 'error')
            conn.close()
            return render_template('auth/register.html')

        hashed_password = generate_password_hash(password)
        cursor = conn.execute(
            '''
            INSERT INTO users (name, email, password, google_id, is_premium)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, email, hashed_password, '', 0))
        user_id = cursor.lastrowid

        conn.commit()
        conn.close()

        session['user_id'] = user_id
        session['user_name'] = name
        session['user_email'] = email
        session['user_picture'] = ''
        session['is_premium'] = 0

        flash(f'Registrasi berhasil! Selamat datang, {name}!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('auth/register.html')


# Google OAuth routes
@app.route('/signin')
def signin():
    if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            oauth_config, scopes=['openid', 'email', 'profile'])
        flow.redirect_uri = url_for('oauth2callback', _external=True)
        authorization_url, state = flow.authorization_url(
            access_type='offline', include_granted_scopes='true')
        session['state'] = state
        return redirect(authorization_url)
    else:
        flash('Google OAuth tidak dikonfigurasi. Silakan daftar manual.',
              'error')
        return redirect(url_for('register'))


@app.route('/oauth2callback')
def oauth2callback():
    state = session['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        oauth_config, scopes=['openid', 'email', 'profile'], state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    request_session = google.auth.transport.requests.Request()

    service = build('oauth2', 'v2', credentials=credentials)
    user_info = service.userinfo().get().execute()

    conn = get_db()
    existing_user = conn.execute('SELECT * FROM users WHERE google_id = ?',
                                 (user_info['id'], )).fetchone()

    if existing_user:
        user_id = existing_user['id']
        is_premium = existing_user['is_premium']
    else:
        cursor = conn.execute(
            'INSERT INTO users (google_id, email, name, picture, is_premium) VALUES (?, ?, ?, ?, ?)',
            (user_info['id'], user_info['email'], user_info['name'],
             user_info.get('picture', ''), 0))
        user_id = cursor.lastrowid
        is_premium = 0

    conn.commit()
    conn.close()

    session['user_id'] = user_id
    session['user_name'] = user_info['name']
    session['user_email'] = user_info['email']
    session['user_picture'] = user_info.get('picture', '')
    session['is_premium'] = is_premium

    flash(f'Selamat datang, {user_info["name"]}!', 'success')
    return redirect(url_for('dashboard'))


@app.route('/signout')
def signout():
    was_admin = 'admin' in session
    session.clear()
    if was_admin:
        flash('Admin telah logout.', 'info')
        return redirect(url_for('admin_login'))
    else:
        flash('Anda telah logout.', 'info')
        return redirect(url_for('index'))


# Main routes
@app.route('/')
def index():
    # Redirect berdasarkan role yang sudah login
    if 'admin' in session:
        return redirect(url_for('admin_dashboard'))
    elif 'user_id' in session:
        return redirect(url_for('dashboard'))
    else:
        try:
            # Get stats for homepage
            conn = get_db()
            stats = {
                'total_invitations':
                conn.execute(
                    'SELECT COUNT(*) FROM wedding_invitations').fetchone()[0],
                'total_users':
                conn.execute('SELECT COUNT(*) FROM users').fetchone()[0],
                'premium_templates':
                conn.execute(
                    'SELECT COUNT(*) FROM wedding_templates WHERE is_premium = 1').
                fetchone()[0],
                'total_guests':
                conn.execute('SELECT COUNT(*) FROM wedding_guests').fetchone()[0]
            }

            # Get sample templates for showcase
            wedding_templates = conn.execute(
                'SELECT * FROM wedding_templates ORDER BY is_premium, name LIMIT 6'
            ).fetchall()
            cv_templates = conn.execute(
                'SELECT * FROM cv_templates ORDER BY is_premium, name LIMIT 6'
            ).fetchall()

            conn.close()

            print(f"Debug Index - Wedding templates count: {len(wedding_templates)}")
            print(f"Debug Index - CV templates count: {len(cv_templates)}")

            return render_template('index.html',
                                   stats=stats,
                                   wedding_templates=wedding_templates,
                                   cv_templates=cv_templates)
        except Exception as e:
            print(f"Error in index route: {str(e)}")
            # Return template with empty data if error
            return render_template('index.html',
                                   stats={'total_invitations': 0, 'total_users': 0, 'premium_templates': 0, 'total_guests': 0},
                                   wedding_templates=[],
                                   cv_templates=[])


@app.route('/dashboard')
@require_auth
def dashboard():
    conn = get_db()

    # Get user's recent wedding invitations
    invitations = conn.execute(
        'SELECT * FROM wedding_invitations WHERE user_id = ? ORDER BY created_at DESC LIMIT 3',
        (session['user_id'], )).fetchall()

    print(
        f"Debug Dashboard - User ID: {session['user_id']}, Found {len(invitations)} invitations"
    )

    # Get user's recent orders
    orders = conn.execute(
        'SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC LIMIT 5',
        (session['user_id'], )).fetchall()

    # Get recent guest messages/wishes for user's invitations
    try:
        # First try with name column
        guest_messages = conn.execute(
            '''
            SELECT wg.name, wg.message, wg.wishes, wg.attendance, wg.created_at, wi.couple_name
            FROM wedding_guests wg
            JOIN wedding_invitations wi ON wg.invitation_id = wi.id
            WHERE wi.user_id = ? AND (wg.message IS NOT NULL AND wg.message != '' OR wg.wishes IS NOT NULL AND wg.wishes != '')
            ORDER BY wg.created_at DESC LIMIT 10
        ''', (session['user_id'], )).fetchall()
    except sqlite3.OperationalError as e:
        print(f"Error getting guest messages: {e}")
        try:
            # Fallback without name column
            guest_messages = conn.execute(
                '''
                SELECT wg.message, wg.wishes, wg.attendance, wg.created_at, wi.couple_name
                FROM wedding_guests wg
                JOIN wedding_invitations wi ON wg.invitation_id = wi.id
                WHERE wi.user_id = ? AND (wg.message IS NOT NULL AND wg.message != '' OR wg.wishes IS NOT NULL AND wg.wishes != '')
                ORDER BY wg.created_at DESC LIMIT 10
            ''', (session['user_id'], )).fetchall()
        except sqlite3.OperationalError:
            guest_messages = []

    conn.close()

    return render_template('dashboard.html',
                           invitations=invitations,
                           orders=orders,
                           guest_messages=guest_messages)


# Order routes for printing services
@app.route('/order', methods=['GET', 'POST'])
def order():
    if request.method == 'POST':
        nama = request.form['nama']
        email = request.form['email']
        whatsapp = request.form['whatsapp']
        jenis_cetakan = request.form['jenis_cetakan']
        ukuran = request.form.get('ukuran', '')
        jumlah = int(request.form['jumlah'])
        warna = request.form.get('warna', '')
        kertas = request.form.get('kertas', '')
        catatan = request.form.get('catatan', '')

        # Handle file upload
        file_path = ''
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                filename = secure_filename(file.filename)
                timestamp = str(int(datetime.now().timestamp()))
                filename = f"{timestamp}_{filename}"
                # Store file in the UPLOAD_FOLDER, which points to PREWEDDING_FOLDER
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                file_path = filename

        conn = get_db()
        conn.execute(
            '''
            INSERT INTO orders (user_id, nama, email, whatsapp, jenis_cetakan, ukuran, jumlah, warna, kertas, catatan, file_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session.get('user_id'), nama, email, whatsapp, jenis_cetakan,
              ukuran, jumlah, warna, kertas, catatan, file_path))
        conn.commit()
        conn.close()

        flash('Pesanan berhasil dibuat! Kami akan segera menghubungi Anda.',
              'success')

        # Redirect based on user login status
        if 'user_id' in session:
            return redirect(url_for('my_orders'))
        else:
            return redirect(url_for('status'))

    return render_template('order.html')


@app.route('/my-orders')
@require_auth
def my_orders():
    conn = get_db()
    orders = conn.execute(
        'SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC',
        (session['user_id'], )).fetchall()
    conn.close()

    return render_template('my_orders.html', orders=orders)


@app.route('/my-guest-messages')
@require_auth
def my_guest_messages():
    """View all guest messages for user's wedding invitations"""
    conn = get_db()

    # Get all guest messages for user's invitations
    guest_messages = conn.execute(
        '''
        SELECT wg.*, wi.couple_name, wi.invitation_link
        FROM wedding_guests wg
        JOIN wedding_invitations wi ON wg.invitation_id = wi.id
        WHERE wi.user_id = ?
        ORDER BY wg.created_at DESC
    ''', (session['user_id'], )).fetchall()

    # Get invitation statistics
    invitation_stats = conn.execute(
        '''
        SELECT wi.id, wi.couple_name, wi.invitation_link,
               COUNT(wg.id) as total_guests,
               SUM(CASE WHEN wg.attendance = 'hadir' THEN 1 ELSE 0 END) as attending,
               SUM(CASE WHEN wg.attendance = 'tidak_hadir' THEN 1 ELSE 0 END) as not_attending,
               SUM(CASE WHEN wg.message IS NOT NULL AND wg.message != '' THEN 1 ELSE 0 END) as with_messages,
               SUM(CASE WHEN wg.wishes IS NOT NULL AND wg.wishes != '' THEN 1 ELSE 0 END) as with_wishes
        FROM wedding_invitations wi
        LEFT JOIN wedding_guests wg ON wi.id = wg.invitation_id
        WHERE wi.user_id = ?
        GROUP BY wi.id, wi.couple_name, wi.invitation_link
        ORDER BY wi.created_at DESC
    ''', (session['user_id'], )).fetchall()

    conn.close()

    return render_template('my_guest_messages.html',
                           guest_messages=guest_messages,
                           invitation_stats=invitation_stats)


@app.route('/status')
def status():
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')

    conn = get_db()
    query = 'SELECT * FROM orders WHERE 1=1'
    params = []

    if search:
        query += ' AND (CAST(id AS TEXT) LIKE ? OR nama LIKE ? OR email LIKE ? OR whatsapp LIKE ?)'
        search_param = f'%{search}%'
        params.extend([search_param, search_param, search_param, search_param])

    if status_filter:
        query += ' AND status = ?'
        params.append(status_filter)

    query += ' ORDER BY created_at DESC'

    orders = conn.execute(query, params).fetchall()
    conn.close()

    return render_template('status.html',
                           orders=orders,
                           search=search,
                           status_filter=status_filter)


# CV Generator routes
@app.route('/cv-generator')
@require_auth
def cv_generator():
    conn = get_db()
    templates = conn.execute(
        'SELECT * FROM cv_templates ORDER BY is_premium, name').fetchall()
    conn.close()

    return render_template('cv_generator.html', templates=templates)


@app.route('/generate-cv', methods=['POST'])
@require_auth
def generate_cv():
    template_id = request.form.get('template_id')

    conn = get_db()
    template = conn.execute('SELECT * FROM cv_templates WHERE id = ?',
                            (template_id, )).fetchone()
    conn.close()

    if not template:
        flash('Template tidak ditemukan!', 'error')
        return redirect(url_for('cv_generator'))

    if template['is_premium'] and not session.get('is_premium'):
        # Double check from database
        try:
            conn_check = get_db()
            user = conn_check.execute('SELECT is_premium, premium_expires_at FROM users WHERE id = ?', 
                                     (session['user_id'],)).fetchone()
            conn_check.close()

            if not user or not user['is_premium']:
                flash(f'Template "{template["name"]}" adalah template premium. Upgrade ke akun premium untuk menggunakan template ini!', 'warning')
                return redirect(url_for('premium_page'))
            else:
                # Update session with current premium status
                session['is_premium'] = True
        except Exception as e:
            print(f"Error checking premium status: {e}")
            flash('Template premium memerlukan akun premium!', 'error')
            return redirect(url_for('premium_page'))

    # Collect CV data
    cv_data = {
        'nama': request.form.get('nama', ''),
        'profesi': request.form.get('profesi', ''),
        'email': request.form.get('email', ''),
        'telepon': request.form.get('telepon', ''),
        'alamat': request.form.get('alamat', ''),
        'ringkasan': request.form.get('ringkasan', ''),
        'pendidikan': [],
        'pengalaman': [],
        'keahlian': request.form.getlist('keahlian')
    }

    # Process education and experience data
    if request.form.getlist('pendidikan_institusi'):
        for i in range(len(request.form.getlist('pendidikan_institusi'))):
            if request.form.getlist('pendidikan_institusi')[i]:
                cv_data['pendidikan'].append({
                    'institusi':
                    request.form.getlist('pendidikan_institusi')[i],
                    'jurusan':
                    request.form.getlist('pendidikan_jurusan')[i] if i < len(
                        request.form.getlist('pendidikan_jurusan')) else '',
                    'tahun':
                    request.form.getlist('pendidikan_tahun')[i] if i < len(
                        request.form.getlist('pendidikan_tahun')) else ''
                })

    if request.form.getlist('pengalaman_perusahaan'):
        for i in range(len(request.form.getlist('pengalaman_perusahaan'))):
            if request.form.getlist('pengalaman_perusahaan')[i]:
                cv_data['pengalaman'].append({
                    'perusahaan':
                    request.form.getlist('pengalaman_perusahaan')[i],
                    'posisi':
                    request.form.getlist('pengalaman_posisi')[i] if i < len(
                        request.form.getlist('pengalaman_posisi')) else '',
                    'periode':
                    request.form.getlist('pengalaman_periode')[i] if i < len(
                        request.form.getlist('pengalaman_periode')) else '',
                    'deskripsi':
                    request.form.getlist('pengalaman_deskripsi')[i] if i < len(
                        request.form.getlist('pengalaman_deskripsi')) else ''
                })

    # Handle photo upload
    foto_base64 = ''
    if 'foto' in request.files:
        foto = request.files['foto']
        if foto.filename != '':
            foto_data = foto.read()
            foto_base64 = base64.b64encode(foto_data).decode()

    cv_data['foto'] = foto_base64

    # Generate QR Code for CV contact
    qr_code_base64 = generate_contact_qr_code(cv_data)
    cv_data['qr_code_base64'] = qr_code_base64

    return render_template('cv_preview.html',
                           cv_data=cv_data,
                           template=template)


# Wedding Invitation routes
@app.route('/wedding-invitations')
@require_auth
def wedding_invitations():
    conn = get_db()
    invitations = conn.execute(
        'SELECT * FROM wedding_invitations WHERE user_id = ? ORDER BY created_at DESC',
        (session['user_id'], )).fetchall()

    # Debug: Print info
    print(f"Debug - User ID: {session['user_id']}")
    print(f"Debug - Found {len(invitations)} invitations")
    for inv in invitations:
        print(f"Debug - Invitation: {inv['couple_name']} (ID: {inv['id']})")

    conn.close()

    return render_template('wedding_invitations.html', invitations=invitations)

# ============================
# Template Access Helper (Global Function)
# ============================
def validate_template_access(user_id, template_id, template_type='wedding'):
    """Database-level template access validation with new subscription system"""
    try:
        conn = get_db()
        conn.execute('PRAGMA busy_timeout = 5000')  # Short timeout, no locks

        # Get template info
        template = conn.execute('SELECT is_premium, price, name FROM wedding_templates WHERE id = ?', 
                               (template_id,)).fetchone()

        if not template:
            conn.close()
            return False, "Template tidak ditemukan"

        # All templates are accessible to paid subscribers (no individual purchases needed)
        if not template['is_premium']:
            conn.close()
            return True, "Template gratis"

        # Check current subscription plan - database level validation
        user = conn.execute('''
            SELECT current_plan, invitation_limit, invitation_count, is_premium 
            FROM users WHERE id = ?
        ''', (user_id,)).fetchone()

        if not user:
            conn.close()
            return False, "User tidak ditemukan"

        # Free users cannot access premium templates
        if not user['is_premium'] or user['current_plan'] == 'free':
            conn.close()
            return False, f"Template premium memerlukan berlangganan. Pilih paket Basic (Rp.35,000), Medium (Rp.50,000), atau Premium (Rp.100,000)"

        # Check if user has active subscription with template access
        active_subscription = conn.execute('''
            SELECT plan_name, has_premium_templates, invitation_limit 
            FROM premium_subscriptions 
            WHERE user_id = ? AND is_active = 1 
            ORDER BY created_at DESC LIMIT 1
        ''', (user_id,)).fetchone()

        if not active_subscription:
            conn.close()
            return False, "Tidak ada berlangganan aktif"

        # All subscription plans now have access to premium templates
        if active_subscription['has_premium_templates']:
            conn.close()
            return True, f"Akses {active_subscription['plan_name']} - Template premium tersedia"

        conn.close()
        return False, "Paket berlangganan tidak mendukung template premium"

    except Exception as e:
        print(f"ACCESS_VALIDATION_ERROR: {e}")
        return False, f"Error sistem: {str(e)}"


@app.route('/create-wedding-invitation', methods=['GET', 'POST'])
@require_auth
def create_wedding_invitation():
    from datetime import datetime
    import uuid
    import json
    import base64
    import os
    from io import BytesIO
    from PIL import Image
    import qrcode
    from werkzeug.utils import secure_filename

    # --------------------------
    # Verify session
    # --------------------------
    if 'user_id' not in session:
        flash('Session expired, silakan login ulang!', 'error')
        return redirect(url_for('login'))

    print(f"Debug - Create Wedding - User ID: {session['user_id']}")
    print(f"Debug - Create Wedding - User Name: {session.get('user_name', 'Unknown')}")

    # --------------------------
    # Handle GET request after template purchase
    # --------------------------
    template_id_param = request.args.get('template_id')
    payment_success = request.args.get('payment_success')
    selected_template_id = None

    if template_id_param and payment_success:
        has_access, message = validate_template_access(session['user_id'], template_id_param, 'wedding')
        if has_access:
            selected_template_id = int(template_id_param)
            flash('🎉 Template premium berhasil dibeli! Silakan buat undangan Anda.', 'success')
        else:
            flash(f'❌ {message}', 'error')
            return redirect(url_for('buy_template', template_id=template_id_param))

    # --------------------------
    # Handle POST request
    # --------------------------
    if request.method == 'POST':
        # Required fields
        bride_name = request.form.get('bride_name', '').strip()
        bride_title = request.form.get('bride_title', '').strip()
        bride_father = request.form.get('bride_father', '').strip()
        bride_mother = request.form.get('bride_mother', '').strip()
        groom_name = request.form.get('groom_name', '').strip()
        groom_title = request.form.get('groom_title', '').strip()
        groom_father = request.form.get('groom_father', '').strip()
        groom_mother = request.form.get('groom_mother', '').strip()

        couple_name = f"{bride_name} & {groom_name}"
        template_id = int(request.form.get('template_id', 1))
        custom_message = request.form.get('custom_message', '')
        guest_limit = int(request.form.get('guest_limit', 100))
        event_type = request.form.get('event_type', 'single')

        # --------------------------
        # Backend Template Access Validation (STRICT - Cannot be bypassed)
        # --------------------------
        has_access, access_message = validate_template_access(session['user_id'], template_id, 'wedding')

        if not has_access:
            print(f"SECURITY: Template access denied for user {session['user_id']}, template {template_id}: {access_message}")
            flash(f'❌ Akses Ditolak: {access_message}', 'error')
            return redirect(url_for('buy_template', template_id=template_id))

        print(f"SECURITY: Template access granted for user {session['user_id']}, template {template_id}: {access_message}")

        # --------------------------
        # Handle event & venue fields
        # --------------------------
        if event_type == 'single':
            wedding_date = request.form.get('wedding_date', '')
            wedding_time = request.form.get('wedding_time', '')
            venue_name = request.form.get('venue_name', '')
            venue_address = request.form.get('venue_address', '')
            akad_date = resepsi_date = wedding_date
            akad_time = resepsi_time = wedding_time
            akad_venue_name = resepsi_venue_name = venue_name
            akad_venue_address = resepsi_venue_address = venue_address
            bride_event_date = bride_event_time = bride_event_venue_name = bride_event_venue_address = ''
            groom_event_date = groom_event_time = groom_event_venue_name = groom_event_venue_address = ''
        else:
            akad_date = request.form.get('akad_date', '')
            akad_time = request.form.get('akad_time', '')
            akad_venue_name = request.form.get('akad_venue_name', '')
            akad_venue_address = request.form.get('akad_venue_address', '')
            resepsi_date = request.form.get('resepsi_date', '')
            resepsi_time = request.form.get('resepsi_time', '')
            resepsi_venue_name = request.form.get('resepsi_venue_name', '')
            resepsi_venue_address = request.form.get('resepsi_venue_address', '')
            bride_event_date = request.form.get('bride_event_date', '')
            bride_event_time = request.form.get('bride_event_time', '')
            bride_event_venue_name = request.form.get('bride_event_venue_name', '')
            bride_event_venue_address = request.form.get('bride_event_venue_address', '')
            groom_event_date = request.form.get('groom_event_date', '')
            groom_event_time = request.form.get('groom_event_time', '')
            groom_event_venue_name = request.form.get('groom_event_venue_name', '')
            groom_event_venue_address = request.form.get('groom_event_venue_address', '')
            # Fallback legacy
            wedding_date = akad_date or resepsi_date
            wedding_time = akad_time or resepsi_time
            venue_name = akad_venue_name or resepsi_venue_name
            venue_address = akad_venue_address or resepsi_venue_address

        bank_name = request.form.get('bank_name', '')
        bank_account = request.form.get('bank_account', '')
        account_holder = request.form.get('account_holder', '')

        # --------------------------
        # Invitation link & QR code
        # --------------------------
        invitation_code = str(uuid.uuid4())[:8]
        invitation_link = f"{bride_name.lower().replace(' ', '')}-{groom_name.lower().replace(' ', '')}-{invitation_code}"

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url_for('view_wedding_invitation', link=invitation_link, _external=True))
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

        # --------------------------
        # Background music
        # --------------------------
        background_music = ''
        music_option = request.form.get('music_option', 'none')
        if music_option == 'default':
            selected_music = request.form.get('default_background_music', '')
            background_music = selected_music or 'default_wedding.mp3'
        elif music_option == 'custom' and 'background_music' in request.files:
            music_file = request.files['background_music']
            if music_file.filename != '':
                filename = secure_filename(music_file.filename)
                timestamp = str(int(datetime.now().timestamp()))
                filename = f"{timestamp}_{filename}"
                music_path = os.path.join(app.config['MUSIC_FOLDER'], filename)
                music_file.save(music_path)
                background_music = filename

        # --------------------------
        # Prewedding photos
        # --------------------------
        prewedding_photos = []
        for i in range(10):
            if f'prewedding_photo_{i}' in request.files:
                photo = request.files[f'prewedding_photo_{i}']
                if photo.filename != '':
                    filename = secure_filename(photo.filename)
                    timestamp = str(int(datetime.now().timestamp()))
                    filename = f"{timestamp}_{i}_{filename}"
                    photo_path = os.path.join(app.config['PREWEDDING_FOLDER'], filename)
                    os.makedirs(app.config['PREWEDDING_FOLDER'], exist_ok=True)
                    photo.save(photo_path)
                    # Detect orientation
                    try:
                        with Image.open(photo_path) as img:
                            width, height = img.size
                            orientation = "portrait" if height > width else "landscape"
                    except:
                        orientation = "landscape"
                    prewedding_photos.append({"filename": filename, "orientation": orientation})

        # --------------------------
        # QRIS upload
        # --------------------------
        qris_code = ''
        if 'qris_code' in request.files:
            qris_file = request.files['qris_code']
            if qris_file.filename != '':
                qris_data = qris_file.read()
                qris_code = base64.b64encode(qris_data).decode()

        # --------------------------
        # Check invitation limit before creating
        # --------------------------
        conn = get_db()
        user_data = conn.execute('''
            SELECT invitation_count, invitation_limit, current_plan, is_premium 
            FROM users WHERE id = ?
        ''', (session['user_id'],)).fetchone()

        if user_data and user_data['is_premium']:
            current_count = user_data['invitation_count'] or 0
            limit = user_data['invitation_limit'] or 0
            
            if limit > 0 and current_count >= limit:
                conn.close()
                flash(f'Batas undangan tercapai! Paket {user_data["current_plan"]} Anda hanya dapat membuat {limit} undangan. Saat ini sudah: {current_count}', 'error')
                return redirect(url_for('wedding_invitations'))
        
        # --------------------------
        # Insert to DB with counter increment
        # --------------------------
        try:
            cursor = conn.execute('''
                INSERT INTO wedding_invitations
                (user_id, couple_name, bride_name, bride_title, bride_father, bride_mother, groom_name, groom_title,
                 groom_father, groom_mother, wedding_date, wedding_time, venue_name, venue_address,
                 template_id, custom_message, invitation_link, qr_code, background_music, prewedding_photos,
                 bank_name, bank_account, account_holder, qris_code, guest_limit,
                 akad_date, akad_time, akad_venue_name, akad_venue_address,
                 resepsi_date, resepsi_time, resepsi_venue_name, resepsi_venue_address,
                 bride_event_date, bride_event_time, bride_event_venue_name, bride_event_venue_address,
                 groom_event_date, groom_event_time, groom_event_venue_name, groom_event_venue_address)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (session['user_id'], couple_name, bride_name, bride_title,
                  bride_father, bride_mother, groom_name, groom_title,
                  groom_father, groom_mother, wedding_date or None,
                  wedding_time or None, venue_name, venue_address, template_id,
                  custom_message, invitation_link, qr_code_base64,
                  background_music, json.dumps(prewedding_photos), bank_name,
                  bank_account, account_holder, qris_code, guest_limit,
                  akad_date or None, akad_time or None, akad_venue_name or None, akad_venue_address or None,
                  resepsi_date or None, resepsi_time or None, resepsi_venue_name or None, resepsi_venue_address or None,
                  bride_event_date or None, bride_event_time or None, bride_event_venue_name or None, bride_event_venue_address or None,
                  groom_event_date or None, groom_event_time or None, groom_event_venue_name or None, groom_event_venue_address or None))
            
            # Increment invitation counter for premium users
            if user_data and user_data['is_premium']:
                conn.execute('''
                    UPDATE users SET invitation_count = COALESCE(invitation_count, 0) + 1 
                    WHERE id = ?
                ''', (session['user_id'],))
                
            conn.commit()
            conn.close()
            flash(f'Undangan pernikahan "{couple_name}" berhasil dibuat!', 'success')
            return redirect(url_for('wedding_invitations'))
        except Exception as e:
            print(f"Database Error: {e}")
            if 'conn' in locals():
                conn.close()
            flash(f"Terjadi kesalahan saat menyimpan undangan: {str(e)}", 'error')
            return redirect(url_for('create_wedding_invitation'))

    # --------------------------
    # Render template for GET
    # --------------------------
    conn = get_db()
    wedding_templates = conn.execute('SELECT * FROM wedding_templates ORDER BY id ASC').fetchall()
    conn.close()
    return render_template('create_wedding_invitation.html',
                           wedding_templates=wedding_templates,
                           selected_template_id=selected_template_id)

@app.route('/wedding/preview-template/<int:template_id>')
def preview_template(template_id):
    try:
        conn = get_db()
        template = conn.execute(
            'SELECT * FROM wedding_templates WHERE id = ?', (template_id,
                                                          )).fetchone()
        conn.close()

        if not template:
            return "Template not found", 404

        # ubah Row → dict agar bisa pakai .get()
        template = dict(template)

        if not template.get("template_file"):
            return "Template file not found", 404

        # ---------- Sample data for preview ----------
        from datetime import datetime
        sample_invitation = {
            'couple_name': 'Desi & Riki',
            'bride_name': 'Desi Apriliani',
            'bride_title': '',
            'bride_father': 'Ano Suparno',
            'bride_mother': 'Nina Rahmawati',
            'groom_name': 'Riki Agus Purwadi',
            'groom_title': '',
            'groom_father': 'Dedi Sulaeman',
            'groom_mother': 'Yulianti',
            'wedding_date': datetime.strptime('2025-10-08', '%Y-%m-%d'),
            'wedding_time': '08:00',
            'venue_name': 'Kediaman Mempelai Wanita',
            'venue_address': 'https://maps.app.goo.gl/njsw3RbBFBAuZcB38',

            # Multi-venue fields
            'akad_date': datetime.strptime('2025-10-08', '%Y-%m-%d'),
            'akad_time': '08:00',
            'akad_venue_name': 'Kediaman Mempelai Wanita',
            'akad_venue_address': 'https://maps.app.goo.gl/njsw3RbBFBAuZcB38',
            'resepsi_date': datetime.strptime('2025-10-08', '%Y-%m-%d'),
            'resepsi_time': '19:00',
            'resepsi_venue_name': 'Kediaman Mempelai Wanita',
            'resepsi_venue_address': 'https://maps.app.goo.gl/njsw3RbBFBAuZcB38',

            # Optional family events
            'bride_event_date': datetime.strptime('2025-10-02', '%Y-%m-%d'),
            'bride_event_time': '10:00',
            'bride_event_venue_name': 'Kediaman Keluarga Mempelai Wanita',
            'bride_event_venue_address': 'https://maps.app.goo.gl/njsw3RbBFBAuZcB38',
            'groom_event_date': datetime.strptime('2025-10-02', '%Y-%m-%d'),
            'groom_event_time': '10:00',
            'groom_event_venue_name': 'Kediaman Keluarga Mempelai Pria',
            'groom_event_venue_address': 'https://maps.app.goo.gl/jBWJ9xTrSBTDNKxq6',

            'custom_message': 'Dengan penuh kebahagiaan, kami mengundang Bapak/Ibu/Saudara/i untuk hadir di acara pernikahan kami.',
            'template_name': template.get('name', 'Unknown Template'),
            'color_scheme': template.get('color_scheme', 'elegant'),
            'animations': template.get('animations', ''),
            'ornaments': template.get('ornaments', ''),
            'background_music': template.get('background_music', ''),
            'bank_name': 'MANDIRI',
            'bank_account': '1320026475575',
            'account_holder': 'Fajar Julyana',
            'qris_code': '',
            'guest_limit': 200,
            'is_active': 1,
            'invitation_link': 'preview-sample',
            'qr_code': '',
            'id': template_id,
            'template_id': template_id
        }

        prewedding_photos = []

        # ---------- Cari file template di folder Documents ----------
        import os, glob
        template_file_raw = template['template_file']
        found_template_path = None

        template_path_docs = os.path.join(app.config['WEDDING_FOLDER'], template_file_raw)
        if os.path.exists(template_path_docs):
            found_template_path = template_path_docs
        else:
            # coba bersihkan prefix angka_timestamp_
            if '_' in template_file_raw:
                parts = template_file_raw.split('_')
                if len(parts) > 1 and parts[0].isdigit():
                    clean_name = '_'.join(parts[1:])
                    clean_path = os.path.join(app.config['WEDDING_FOLDER'], clean_name)
                    if os.path.exists(clean_path):
                        found_template_path = clean_path
            # coba pattern matching
            if not found_template_path:
                pattern = os.path.join(app.config['WEDDING_FOLDER'], f"*{template_file_raw}")
                matches = glob.glob(pattern)
                if matches:
                    found_template_path = matches[0]

        if not found_template_path:
            return render_template_string("""
                <div style="padding: 2rem; text-align: center;">
                    <h4>Template tidak ditemukan</h4>
                    <p>File template '{{ template_file }}' tidak ditemukan di folder.</p>
                    <p>Path: {{ folder }}</p>
                </div>
                """,
                template_file=template_file_raw,
                folder=app.config['WEDDING_FOLDER'])

        # ---------- Render template ----------
        with open(found_template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()

        return render_template_string(template_content,
                                      invitation=sample_invitation,
                                      guests=[],
                                      prewedding_photos=prewedding_photos)

    except Exception as e:
        print(f"ERROR PREVIEW: {str(e)}")
        return f"Internal Server Error: {str(e)}", 500


@app.route('/thumbnails/<path:filename>')
def serve_thumbnail(filename):
    """Serve thumbnails from Documents folder"""
    thumbnail_path = os.path.join(USER_DOCS, 'thumbnails', filename)
    if os.path.exists(thumbnail_path):
        return send_file(thumbnail_path)
    else:
        # Try static/images folder
        static_path = os.path.join('static/images', filename)
        if os.path.exists(static_path):
            return send_file(static_path, as_attachment=False)
        else:
            # Generate a simple placeholder thumbnail
            try:
                from PIL import Image, ImageDraw, ImageFont
                img = Image.new('RGB', (300, 200), color='#f0f0f0')
                draw = ImageDraw.Draw(img)
                draw.rectangle([10, 10, 290, 190], outline='#ddd', width=2)
                draw.text((120, 90), 'No Preview', fill='#666')

                # Save to memory and return
                from io import BytesIO
                buffer = BytesIO()
                img.save(buffer, format='JPEG')
                buffer.seek(0)

                return send_file(buffer, mimetype='image/jpeg')
            except Exception:
                # Ultimate fallback - return 404
                abort(404)


@app.route('/api/wedding-templates')
def api_wedding_templates():
    """API endpoint for wedding templates"""
    conn = get_db()
    templates = conn.execute(
        'SELECT * FROM wedding_templates ORDER BY is_premium, name').fetchall(
        )
    conn.close()

    templates_list = []
    for template in templates:
        templates_list.append({
            'id':
            template['id'],
            'name':
            template['name'],
            'description':
            template['description'],
            'category':
            template['category'],
            'preview_image':
            f"/thumbnails/wedding_templates/{template['preview_image']}"
            if template['preview_image'] else
            '/static/images/wedding_templates/default_preview.jpg',
            'is_premium':
            bool(template['is_premium']),
            'price':
            template['price'] or 0,
            'color_scheme':
            template['color_scheme'],
            'animations':
            template['animations']
        })

    return jsonify(templates_list)


@app.route('/wedding/<link>')
def view_wedding_invitation(link):
    conn = get_db()
    invitation = conn.execute(
        '''SELECT wi.*, wt.name as template_name, wt.color_scheme, wt.animations, wt.ornaments, wt.template_file
           FROM wedding_invitations wi
           LEFT JOIN wedding_templates wt ON wi.template_id = wt.id
           WHERE wi.invitation_link = ? AND wi.is_active = 1''',
        (link, )).fetchone()

    if not invitation:
        return render_template('404.html'), 404

    guests = conn.execute(
        'SELECT * FROM wedding_guests WHERE invitation_id = ? ORDER BY created_at DESC',
        (invitation['id'], )).fetchall()

    conn.close()

    # Convert invitation to dict for manipulation
    invitation_dict = dict(invitation)

    # Convert wedding_date string to datetime object if it exists
    if invitation_dict.get('wedding_date'):
        try:
            from datetime import datetime
            invitation_dict['wedding_date'] = datetime.strptime(
                invitation_dict['wedding_date'], '%Y-%m-%d')
        except (ValueError, TypeError):
            invitation_dict['wedding_date'] = None

    # Convert other date fields if they exist
    for date_field in [
            'akad_date', 'resepsi_date', 'bride_event_date', 'groom_event_date'
    ]:
        if invitation_dict.get(date_field):
            try:
                invitation_dict[date_field] = datetime.strptime(
                    invitation_dict[date_field], '%Y-%m-%d')
            except (ValueError, TypeError):
                invitation_dict[date_field] = None

    # Parse prewedding photos with enhanced debugging
    prewedding_photos = []
    if invitation_dict['prewedding_photos']:
        try:
            prewedding_photos = json.loads(
                invitation_dict['prewedding_photos'])
            print(
                f"DEBUG PHOTOS: Found {len(prewedding_photos)} prewedding photos"
            )
            for i, photo in enumerate(prewedding_photos):
                if isinstance(photo, dict):
                    print(
                        f"  Photo {i+1}: {photo.get('filename', 'no filename')} ({photo.get('orientation', 'no orientation')})"
                    )
                else:
                    print(f"  Photo {i+1}: {photo} (old format)")
        except Exception as e:
            print(f"DEBUG PHOTOS: Error parsing prewedding photos: {str(e)}")
            prewedding_photos = []
    else:
        print("DEBUG PHOTOS: No prewedding photos data found")

    # Debug template selection
    print(f"DEBUG: Template ID: {invitation_dict.get('template_id')}")
    print(
        f"DEBUG: Template file from DB: {invitation_dict.get('template_file')}")

    # Render template yang sesuai dengan template yang dipilih
    template_file = invitation_dict.get('template_file')

    # If no template file specified, show error
    if not template_file:
        print(
            f"ERROR: No template file specified for invitation {invitation_dict.get('id')}"
        )
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Template Tidak Ditemukan</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 2rem; }
                .error-container { max-width: 500px; margin: 0 auto; }
                .error-icon { font-size: 4rem; color: #e74c3c; margin-bottom: 1rem; }
                h1 { color: #e74c3c; }
                p { color: #666; line-height: 1.6; }
            </style>
        </head>
        <body>
            <div class="error-container">
                <div class="error-icon">⚠️</div>
                <h1>No Template Specified</h1>
                <p>No template file has been specified for this invitation.</p>
                <p>Please select a template to preview the invitation.</p>
            </div>
        </body>
        </html>
        """), 404

    # PRIORITAS: Check ONLY Documents folder first
    import os
    import glob
    template_file_raw = invitation_dict.get('template_file')

    found_template_path = None

    if template_file_raw:
        # Check template di Documents/FajarMandiriStore/wedding_templates
        template_path_docs = os.path.join(app.config['WEDDING_FOLDER'], template_file_raw)

        print(f"DEBUG: Checking Documents path: {template_path_docs}")

        if os.path.exists(template_path_docs):
            found_template_path = template_path_docs
            print(f"DEBUG: Found template in Documents: {template_path_docs}")
        else:
            # Coba cari file dengan pattern untuk menghilangkan timestamp prefix
            if '_' in template_file_raw:
                # Hapus timestamp prefix
                parts = template_file_raw.split('_')
                if len(parts) > 1 and parts[0].isdigit():
                    clean_name = '_'.join(parts[1:])
                    clean_path = os.path.join(app.config['WEDDING_FOLDER'], clean_name)
                    print(f"DEBUG: Trying clean name: {clean_path}")
                    if os.path.exists(clean_path):
                        found_template_path = clean_path
                        print(f"DEBUG: Found clean template in Documents: {clean_path}")

            # Jika masih tidak ada, cari dengan pattern matching
            if not found_template_path:
                pattern = os.path.join(app.config['WEDDING_FOLDER'], f"*{template_file_raw}")
                matches = glob.glob(pattern)
                if matches:
                    found_template_path = matches[0]
                    print(f"DEBUG: Found template via pattern: {found_template_path}")
                else:
                    # Coba pattern tanpa timestamp
                    if '_' in template_file_raw:
                        base_name = template_file_raw.replace('.html', '')
                        parts = base_name.split('_')
                        if len(parts) > 1 and parts[0].isdigit():
                            clean_base = '_'.join(parts[1:])
                            pattern2 = os.path.join(app.config['WEDDING_FOLDER'], f"*{clean_base}.html")
                            matches2 = glob.glob(pattern2)
                            if matches2:
                                found_template_path = matches2[0]
                                print(f"DEBUG: Found template via clean pattern: {found_template_path}")

    if not found_template_path:
        print(f"ERROR: Template file not found in Documents folder: {template_file_raw}")
        return render_template_string("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Template Tidak Ditemukan</title>
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; padding: 2rem; }
                    .error-container { max-width: 500px; margin: 0 auto; }
                    .error-icon { font-size: 4rem; color: #e74c3c; margin-bottom: 1rem; }
                    h1 { color: #e74c3c; }
                    p { color: #666; line-height: 1.6; }
                    .details { background: #f8f9fa; padding: 1rem; border-radius: 5px; margin-top: 1rem; }
                </style>
            </head>
            <body>
                <div class="error-container">
                    <div class="error-icon">📄</div>
                    <h1>Template Tidak Ditemukan</h1>
                    <p>File template tidak ditemukan di Documents/FajarMandiriStore/wedding_templates/</p>
                    <div class="details">
                        <p><strong>Template:</strong> {{ template_file }}</p>
                        <p><strong>Folder:</strong> {{ folder }}</p>
                    </div>
                </div>
            </body>
            </html>
            """,
            template_file=template_file_raw,
            folder=app.config['WEDDING_FOLDER']), 404

    try:
        # Load template dari Documents folder
        print(f"DEBUG: Loading template from Documents: {found_template_path}")
        with open(found_template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()

        return render_template_string(template_content,
                                      invitation=invitation_dict,
                                      guests=guests,
                                      prewedding_photos=prewedding_photos)

    except Exception as e:
        print(f"ERROR: Failed to load template from Documents: {str(e)}")
        # Fallback to basic wedding invitation view
        try:
            return render_template('wedding_invitation_view.html',
                                   invitation=invitation_dict,
                                   guests=guests,
                                   prewedding_photos=prewedding_photos)
        except Exception as e2:
            print(f"ERROR: Even fallback failed: {str(e2)}")
            return render_template_string("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Error Loading Template</title>
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; padding: 2rem; }
                    .error-container { max-width: 600px; margin: 0 auto; }
                    .error-icon { font-size: 4rem; color: #e74c3c; margin-bottom: 1rem; }
                    h1 { color: #e74c3c; }
                    p { color: #666; line-height: 1.6; }
                    .details { background: #f8f9fa; padding: 1rem; border-radius: 5px; margin-top: 1rem; text-align: left; }
                </style>
            </head>
            <body>
                <div class="error-container">
                    <div class="error-icon">❌</div>
                    <h1>Template Error</h1>
                    <p>Terjadi kesalahan saat memuat template undangan.</p>
                    <div class="details">
                        <p><strong>Template:</strong> {{ template_file }}</p>
                        <p><strong>Error:</strong> {{ error }}</p>
                        <p><strong>Couple:</strong> {{ couple_name }}</p>
                    </div>
                </div>
            </body>
            </html>
            """,
                                          template_file=found_template_path,
                                          error=str(e),
                                          couple_name=invitation_dict.get(
                                              'couple_name', 'Unknown')), 500


@app.route('/edit-wedding-invitation/<int:id>')
@require_admin
def edit_wedding_invitation(id):
    """Edit wedding invitation (placeholder)"""
    flash('Fitur edit undangan sedang dalam pengembangan', 'info')
    return redirect(url_for('wedding_invitations'))


@app.route('/manage-guests/<int:invitation_id>')
@require_admin
def manage_guests(invitation_id):
    """Manage wedding guests (placeholder)"""
    flash('Fitur kelola tamu sedang dalam pengembangan', 'info')
    return redirect(url_for('wedding_invitations'))


@app.route('/invitation-analytics/<int:invitation_id>')
@require_admin
def invitation_analytics(invitation_id):
    """View invitation analytics (placeholder)"""
    flash('Fitur analytics sedang dalam pengembangan', 'info')
    return redirect(url_for('wedding_invitations'))


@app.route('/toggle-invitation-status/<int:invitation_id>')
@require_auth
def toggle_invitation_status(invitation_id):
    conn = get_db()
    invitation = conn.execute(
        'SELECT * FROM wedding_invitations WHERE id = ? AND user_id = ?',
        (invitation_id, session['user_id'])).fetchone()

    if not invitation:
        flash('Undangan tidak ditemukan!', 'error')
        return redirect(url_for('wedding_invitations'))

    new_status = 0 if invitation['is_active'] else 1
    conn.execute('UPDATE wedding_invitations SET is_active = ? WHERE id = ?',
                 (new_status, invitation_id))
    conn.commit()
    conn.close()

    status_text = 'diaktifkan' if new_status else 'dinonaktifkan'
    flash(f'Undangan berhasil {status_text}!', 'success')
    return redirect(url_for('wedding_invitations'))


@app.route('/delete-invitation/<int:invitation_id>')
@require_auth
def delete_invitation(invitation_id):
    conn = get_db()
    invitation = conn.execute(
        'SELECT * FROM wedding_invitations WHERE id = ? AND user_id = ?',
        (invitation_id, session['user_id'])).fetchone()

    if not invitation:
        flash('Undangan tidak ditemukan!', 'error')
        return redirect(url_for('wedding_invitations'))

    # Delete associated guests first
    conn.execute('DELETE FROM wedding_guests WHERE invitation_id = ?',
                 (invitation_id, ))
    # Delete invitation
    conn.execute('DELETE FROM wedding_invitations WHERE id = ?',
                 (invitation_id, ))
    conn.commit()
    conn.close()

    flash('Undangan berhasil dihapus!', 'success')
    return redirect(url_for('wedding_invitations'))


@app.route('/rsvp/<int:invitation_id>', methods=['POST'])
def rsvp_wedding(invitation_id):
    name = request.form['name']
    phone = request.form.get('phone', '')
    email = request.form.get('email', '')
    attendance = request.form['attendance']
    guest_count = int(request.form.get('guest_count', 1))
    message = request.form.get('message', '')
    wishes = request.form.get('wishes', '')

    conn = get_db()
    conn.execute(
        '''
        INSERT INTO wedding_guests (invitation_id, name, phone, email, attendance, guest_count, message, wishes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (invitation_id, name, phone, email, attendance, guest_count, message,
          wishes))
    conn.commit()
    conn.close()

    flash('Terima kasih atas konfirmasi kehadiran Anda!', 'success')
    return redirect(request.referrer)


# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
@require_guest_only
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        admin = conn.execute('SELECT * FROM admin WHERE username = ?',
                             (username, )).fetchone()
        conn.close()

        if admin and check_password_hash(admin['password'], password):
            session['admin'] = True
            session['admin_username'] = username
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Username atau password salah!', 'error')

    return render_template('admin/login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    session.pop('admin_username', None)
    return redirect(url_for('index'))


@app.route('/admin')
@require_admin
def admin_dashboard():
    conn = get_db()

    total_users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    total_invitations = conn.execute(
        'SELECT COUNT(*) FROM wedding_invitations').fetchone()[0]
    total_cv_templates = conn.execute(
        'SELECT COUNT(*) FROM cv_templates').fetchone()[0]
    total_wedding_templates = conn.execute(
        'SELECT COUNT(*) FROM wedding_templates').fetchone()[0]
    total_orders = conn.execute('SELECT COUNT(*) FROM orders').fetchone()[0]
    pending_orders = conn.execute(
        'SELECT COUNT(*) FROM orders WHERE status = "Pending"').fetchone()[0]

    stats = {
        'total_users': total_users,
        'total_invitations': total_invitations,
        'total_cv_templates': total_cv_templates,
        'total_wedding_templates': total_wedding_templates,
        'total_orders': total_orders,
        'pending_orders': pending_orders
    }

    conn.close()

    return render_template('admin/dashboard.html', stats=stats)


@app.route('/admin/cv-templates', methods=['GET', 'POST'])
@require_admin
def admin_cv_templates():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']
        color_scheme = request.form['color_scheme']
        animations = request.form['animations']
        is_premium = 1 if request.form.get('is_premium') else 0

        # Handle file uploads
        template_file = ''
        preview_image = ''

        if 'template_file' in request.files:
            file = request.files['template_file']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['TEMPLATES_FOLDER'],
                                         filename)
                file.save(file_path)
                template_file = filename

        if 'preview_image' in request.files:
            file = request.files['preview_image']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['TEMPLATES_FOLDER'],
                                         filename)
                file.save(file_path)
                preview_image = filename

        conn = get_db()
        conn.execute(
            '''
            INSERT INTO cv_templates (name, description, category, template_file, preview_image, color_scheme, animations, is_premium)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, description, category, template_file, preview_image,
              color_scheme, animations, is_premium))
        conn.commit()
        conn.close()

        flash('Template CV berhasil ditambahkan!', 'success')
        return redirect(url_for('admin_cv_templates'))

    conn = get_db()
    templates = conn.execute(
        'SELECT * FROM cv_templates ORDER BY created_at DESC').fetchall()
    conn.close()

    return render_template('admin/cv_templates.html', templates=templates)


@app.route('/admin/download-base-template')
@require_admin
def download_base_template():
    """Download base template for theme development"""
    try:
        template_path = os.path.join('templates', 'admin',
                                     'base_template.html')
        return send_file(template_path,
                         as_attachment=True,
                         download_name='wedding_base_template.html')
    except Exception as e:
        flash(f'Error downloading template: {str(e)}', 'error')
        return redirect(url_for('admin_wedding_templates'))


@app.route('/admin/theme-guide')
@require_admin
def admin_theme_guide():
    """Show theme development guide"""
    return render_template('admin/theme_development_guide.html')


@app.route('/admin/generate-thumbnail/<int:template_id>')
@require_admin
def generate_template_thumbnail(template_id):
    """Generate thumbnail for a specific template"""
    conn = get_db()
    template = conn.execute('SELECT * FROM wedding_templates WHERE id = ?',
                            (template_id, )).fetchone()

    if not template:
        flash('Template tidak ditemukan!', 'error')
        return redirect(url_for('admin_wedding_templates'))

    # Generate thumbnail
    thumbnail_filename = generate_thumbnail_from_template(
        template['id'],
        template['name'],
        template['color_scheme'],
        template['template_file']  # tambahkan ini
    )

    if thumbnail_filename:
        # Update database with new thumbnail
        conn.execute(
            'UPDATE wedding_templates SET preview_image = ? WHERE id = ?',
            (thumbnail_filename, template_id))
        conn.commit()
        flash(
            f'Thumbnail berhasil digenerate untuk template {template["name"]}!',
            'success')
    else:
        flash('Gagal generate thumbnail!', 'error')

    conn.close()
    return redirect(url_for('admin_wedding_templates'))


@app.route('/admin/demo-template/<int:template_id>')
@require_admin
def admin_demo_template(template_id):
    """Admin demo route for wedding templates"""
    return preview_template(template_id)


@app.route('/admin/generate-all-thumbnails')
@require_admin
def generate_all_thumbnails():
    """Generate thumbnails for all templates"""
    conn = get_db()
    templates = conn.execute('SELECT * FROM wedding_templates').fetchall()

    success_count = 0
    total_count = len(templates)

    for template in templates:
        thumbnail_filename = generate_thumbnail_from_template(
            template['id'],
            template['name'],
            template['color_scheme'],
            template['template_file']  # tambahkan ini
        )

        if thumbnail_filename:
            conn.execute(
                'UPDATE wedding_templates SET preview_image = ? WHERE id = ?',
                (thumbnail_filename, template['id']))
            success_count += 1

    conn.commit()
    conn.close()

    flash(f'Berhasil generate {success_count} dari {total_count} thumbnails!',
          'success')
    return redirect(url_for('admin_wedding_templates'))


def generate_thumbnail_from_template(template_id, template_name, color_scheme, template_file):
    """Generate thumbnail khusus wedding template dengan fallback ke simple generator"""
    try:
        # Try selenium approach first
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from PIL import Image
        import time

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1200,800")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")

        driver = webdriver.Chrome(options=chrome_options)

        # Buka halaman preview wedding template
        url = f"http://localhost:5001/preview-thumbnail/{template_id}"
        driver.get(url)

        # Wait for page to load
        time.sleep(3)

        try:
            # Try different selectors for content
            selectors = [
                ".invitation-container",
                ".wedding-invitation",
                ".content-section",
                ".hero-section",
                "body"
            ]

            element = None
            for selector in selectors:
                try:
                    element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue

            if element:
                screenshot = element.screenshot_as_png
            else:
                screenshot = driver.get_screenshot_as_png()

        except Exception:
            print(f"[Thumbnail Warning] Using full page screenshot for template {template_file}")
            screenshot = driver.get_screenshot_as_png()

        image = Image.open(BytesIO(screenshot))
        image.thumbnail((400, 300), Image.Resampling.LANCZOS)

        timestamp = str(int(datetime.now().timestamp()))
        thumbnail_filename = f"{timestamp}_template_{template_id}_thumbnail.jpg"
        thumbnail_path = os.path.join(app.config['WEDDING_THUMBNAILS_FOLDER'],
                                      thumbnail_filename)
        os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)

        image.convert("RGB").save(thumbnail_path, "JPEG", quality=85)

        driver.quit()
        return thumbnail_filename

    except Exception as e:
        print(
            f"[Thumbnail Error] Selenium failed for template {template_file} (ID {template_id}): {e}"
        )
        if 'driver' in locals():
            try:
                driver.quit()
            except:
                pass

        # Fallback to simple image generation
        return generate_simple_wedding_thumbnail(template_id, template_name,
                                                 color_scheme)


def generate_simple_wedding_thumbnail(template_id, template_name,
                                      color_scheme):
    """Generate simple wedding thumbnail using PIL"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        import random

        # Create a wedding-themed thumbnail
        width, height = 400, 300

        # Wedding color schemes
        color_schemes = {
            'elegant': ['#f8f9fa', '#d4af37', '#8b4513'],
            'romantic': ['#fef7f7', '#ff69b4', '#8b008b'],
            'classic': ['#ffffff', '#000000', '#696969'],
            'garden': ['#f0fff0', '#228b22', '#006400'],
            'modern': ['#f5f5f5', '#4169e1', '#191970'],
            'cream': ['#fffdd0', '#daa520', '#b8860b']
        }

        colors = color_schemes.get(color_scheme, color_schemes['elegant'])
        bg_color = colors[0]
        primary_color = colors[1]
        accent_color = colors[2]

        # Create image
        img = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(img)

        # Wedding elements
        # Header decorative border
        draw.rectangle([0, 0, width, 40], fill=primary_color)
        draw.rectangle([0, height - 40, width, height], fill=primary_color)

        # Center heart or rings
        center_x, center_y = width // 2, height // 2

        # Draw wedding rings or heart
        if random.choice([True, False]):
            # Draw heart shape (simplified)
            heart_size = 30
            draw.ellipse([
                center_x - heart_size, center_y - 15, center_x, center_y + 15
            ],
                         fill=accent_color)
            draw.ellipse([
                center_x, center_y - 15, center_x + heart_size, center_y + 15
            ],
                         fill=accent_color)
        else:
            # Draw wedding rings
            ring_size = 25
            draw.ellipse([
                center_x - 40, center_y - ring_size,
                center_x - 40 + ring_size * 2, center_y + ring_size
            ],
                         outline=accent_color,
                         width=4)
            draw.ellipse([
                center_x + 15, center_y - ring_size,
                center_x + 15 + ring_size * 2, center_y + ring_size
            ],
                         outline=accent_color,
                         width=4)

        # Decorative elements
        for i in range(3):
            y_pos = 80 + (i * 30)
            draw.rectangle([50, y_pos, width - 50, y_pos + 8],
                           fill=primary_color)
            draw.rectangle([80, y_pos + 15, width - 80, y_pos + 20],
                           fill=accent_color)

        # Template name indicator
        name_width = min(len(template_name) * 8, width - 20)
        draw.rectangle([10, height - 30, 10 + name_width, height - 20],
                       fill=accent_color)

        # Save thumbnail
        timestamp = str(int(datetime.now().timestamp()))
        thumbnail_filename = f"{timestamp}_simple_template_{template_id}_thumbnail.jpg"
        thumbnail_path = os.path.join(app.config['WEDDING_THUMBNAILS_FOLDER'],
                                      thumbnail_filename)
        os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)

        img.save(thumbnail_path, "JPEG", quality=85)
        return thumbnail_filename

    except Exception as e:
        print(
            f"[Simple Thumbnail Error] Template {template_name} (ID {template_id}): {e}"
        )
        return None


@app.route('/admin/generate-cv-thumbnail/<int:template_id>')
@require_admin
def generate_cv_template_thumbnail(template_id):
    """Generate thumbnail for a specific CV template"""
    conn = get_db()
    template = conn.execute('SELECT * FROM cv_templates WHERE id = ?',
                            (template_id, )).fetchone()

    if not template:
        flash('Template tidak ditemukan!', 'error')
        return redirect(url_for('admin_cv_templates'))

    # Generate thumbnail for CV with category info
    thumbnail_filename = generate_cv_thumbnail_simple(template['id'],
                                                      template['name'],
                                                      template['color_scheme'],
                                                      template['category'])

    if thumbnail_filename:
        # Update database with new thumbnail
        conn.execute('UPDATE cv_templates SET preview_image = ? WHERE id = ?',
                     (thumbnail_filename, template_id))
        conn.commit()
        flash(
            f'Thumbnail berhasil digenerate untuk template {template["name"]}!',
            'success')
    else:
        flash('Gagal generate thumbnail!', 'error')

    conn.close()
    return redirect(url_for('admin_cv_templates'))


@app.route('/admin/generate-all-cv-thumbnails')
@require_admin
def generate_all_cv_thumbnails():
    """Generate thumbnails for all CV templates"""
    conn = get_db()
    templates = conn.execute('SELECT * FROM cv_templates').fetchall()

    success_count = 0
    total_count = len(templates)

    for template in templates:
        thumbnail_filename = generate_cv_thumbnail_simple(
            template['id'], template['name'], template['color_scheme'],
            template['category'])

        if thumbnail_filename:
            conn.execute(
                'UPDATE cv_templates SET preview_image = ? WHERE id = ?',
                (thumbnail_filename, template['id']))
            success_count += 1

    conn.commit()
    conn.close()

    flash(
        f'Berhasil generate {success_count} dari {total_count} CV thumbnails!',
        'success')
    return redirect(url_for('admin_cv_templates'))


@app.route('/admin/wedding-templates', methods=['GET', 'POST'])
@require_admin
def admin_wedding_templates():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']
        color_scheme = request.form['color_scheme']
        animations = request.form['animations']
        ornaments = request.form['ornaments']
        is_premium = 1 if request.form.get('is_premium') else 0
        price = int(request.form.get('price', 0))

        # Handle file uploads
        template_file = ''
        background_music = ''

        # save HTML template
        if 'template_file' in request.files:
            file = request.files['template_file']
            if file.filename != '':
                filename = secure_filename(file.filename)
                timestamp = str(int(datetime.now().timestamp()))
                filename = f"{timestamp}_{filename}"
                file_path = os.path.join(app.config['WEDDING_FOLDER'],
                                         filename)
                file.save(file_path)
                template_file = filename

        # save background music
        if 'background_music' in request.files:
            file = request.files['background_music']
            if file.filename != '':
                filename = secure_filename(file.filename)
                timestamp = str(int(datetime.now().timestamp()))
                filename = f"{timestamp}_{filename}"
                file_path = os.path.join(app.config['MUSIC_FOLDER'],
                                         filename)
                file.save(file_path)
                background_music = filename

        conn = get_db()
        conn.execute(
            '''
            INSERT INTO wedding_templates
            (name, description, category, template_file, preview_image, color_scheme, animations, background_music, ornaments, is_premium, price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, description, category, template_file, '', color_scheme,
              animations, background_music, ornaments, is_premium, price))
        conn.commit()
        conn.close()

        flash('Template wedding berhasil ditambahkan!', 'success')

        return redirect(url_for('admin_wedding_templates'))

    conn = get_db()
    templates = conn.execute(
        'SELECT * FROM wedding_templates ORDER BY created_at DESC').fetchall()
    conn.close()

    return render_template('admin/wedding_templates.html', templates=templates)


@app.route('/admin/users')
@require_admin
def admin_users():
    conn = get_db()
    users = conn.execute(
        'SELECT * FROM users ORDER BY created_at DESC').fetchall()
    conn.close()

    return render_template('admin/users.html', users=users)


@app.route('/admin/toggle-premium/<int:user_id>')
@require_admin
def admin_toggle_premium(user_id):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?',
                        (user_id, )).fetchone()

    if not user:
        flash('User tidak ditemukan!', 'error')
        return redirect(url_for('admin_users'))

    new_premium_status = 0 if user['is_premium'] else 1
    conn.execute('UPDATE users SET is_premium = ? WHERE id = ?',
                 (new_premium_status, user_id))
    conn.commit()
    conn.close()

    status_text = 'Premium' if new_premium_status else 'Regular'
    flash(f'Status {user["name"]} berhasil diubah menjadi {status_text}!',
          'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/ban-user/<int:user_id>', methods=['POST'])
@require_admin
def admin_ban_user(user_id):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id, )).fetchone()

    if not user:
        flash('User tidak ditemukan!', 'error')
        return redirect(url_for('admin_users'))

    ban_reason = request.form.get('ban_reason', 'Pelanggaran kebijakan')
    user_dict = dict(user)
    new_ban_status = 0 if user_dict.get('is_banned') else 1

    conn.execute('UPDATE users SET is_banned = ?, ban_reason = ? WHERE id = ?',
                 (new_ban_status, ban_reason if new_ban_status else None, user_id))
    conn.commit()
    conn.close()

    action = 'dibanned' if new_ban_status else 'unbanned'
    flash(f'User {user["name"]} berhasil {action}!', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/block-user/<int:user_id>')
@require_admin
def admin_block_user(user_id):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id, )).fetchone()

    if not user:
        flash('User tidak ditemukan!', 'error')
        return redirect(url_for('admin_users'))

    user_dict = dict(user)
    new_block_status = 0 if user_dict.get('is_blocked') else 1
    conn.execute('UPDATE users SET is_blocked = ? WHERE id = ?',
                 (new_block_status, user_id))
    conn.commit()
    conn.close()

    action = 'diblokir' if new_block_status else 'unblocked'
    flash(f'User {user["name"]} berhasil {action}!', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/delete-user/<int:user_id>', methods=['POST'])
@require_admin
def admin_delete_user(user_id):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id, )).fetchone()

    if not user:
        flash('User tidak ditemukan!', 'error')
        return redirect(url_for('admin_users'))

    # Check if user has any active orders or invitations
    active_orders = conn.execute('SELECT COUNT(*) FROM orders WHERE user_id = ?', (user_id, )).fetchone()[0]
    active_invitations = conn.execute('SELECT COUNT(*) FROM wedding_invitations WHERE user_id = ?', (user_id, )).fetchone()[0]

    if active_orders > 0 or active_invitations > 0:
        flash(f'Tidak dapat menghapus user {user["name"]} karena masih memiliki pesanan atau undangan aktif!', 'error')
        return redirect(url_for('admin_users'))

    # Delete user and related data
    conn.execute('DELETE FROM premium_subscriptions WHERE user_id = ?', (user_id, ))
    conn.execute('DELETE FROM payments WHERE user_id = ?', (user_id, ))
    conn.execute('DELETE FROM users WHERE id = ?', (user_id, ))
    conn.commit()
    conn.close()

    flash(f'User {user["name"]} berhasil dihapus!', 'success')
    return redirect(url_for('admin_users'))


# ========== MIDTRANS PAYMENT INTEGRATION ==========

@app.route('/premium')
@require_auth
def premium_page():
    """Premium subscription page"""
    return render_template('premium.html')


@app.route('/buy-template/<int:template_id>')
@require_auth
def buy_template(template_id):
    """Direct purchase for premium template"""
    conn = get_db()
    template = conn.execute('SELECT * FROM wedding_templates WHERE id = ? AND is_premium = 1', 
                           (template_id,)).fetchone()
    conn.close()

    if not template:
        flash('Template tidak ditemukan atau bukan template premium!', 'error')
        return redirect(url_for('create_wedding_invitation'))

    return render_template('buy_template.html', template=template)


@app.route('/create-template-payment', methods=['POST'])
@require_auth
def create_template_payment():
    """Create payment for individual template purchase"""
    import requests
    import json
    import base64
    from datetime import datetime

    template_id = request.form.get('template_id')
    user_id = session['user_id']

    if not template_id:
        flash('Template ID tidak valid!', 'error')
        return redirect(url_for('create_wedding_invitation'))

    try:
        conn = get_db()
        template = conn.execute(
            'SELECT * FROM wedding_templates WHERE id = ? AND is_premium = 1', 
            (template_id,)
        ).fetchone()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

        if not template:
            flash('Template tidak ditemukan atau bukan template premium!', 'error')
            return redirect(url_for('create_wedding_invitation'))
        if not user:
            flash('User tidak ditemukan!', 'error')
            return redirect(url_for('login'))

        amount = template['price'] or 35000
        order_id = f"TEMPLATE-{template_id}-{user_id}-{int(datetime.now().timestamp())}"

        # Simpan data payment awal
        try:
            conn.execute("""
                INSERT INTO payments (order_id, user_id, template_id, payment_type, status, amount, created_at)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            """, (order_id, user_id, template_id, f'template_{template_id}', 'pending', amount))
            conn.commit()
            print(f"[INFO] Payment record inserted for template order {order_id}")
        except Exception as e:
            print(f"[ERROR] Failed to insert payment record for order {order_id}: {e}")

        # Midtrans configuration
        midtrans_server_key = os.getenv("MIDTRANS_SERVER_KEY")
        midtrans_client_key = os.getenv("MIDTRANS_CLIENT_KEY")
        is_production = False
        snap_url = 'https://app.sandbox.midtrans.com/snap/v1/transactions'

        transaction_data = {
            "transaction_details": {"order_id": order_id, "gross_amount": amount},
            "customer_details": {"first_name": user['name'], "email": user['email'], "phone": "081234567890"},
            "item_details": [{
                "id": f"template-{template_id}",
                "price": amount,
                "quantity": 1,
                "name": f"Template Premium: {template['name']}"
            }],
            "callbacks": {
                "finish": f"{request.url_root}payment/finish?order_id={order_id}",
                "unfinish": f"{request.url_root}payment/unfinish?order_id={order_id}",
                "error": f"{request.url_root}payment/error?order_id={order_id}"
            },
            "enabled_payments": [
                "credit_card", "bca_va", "bni_va", "bri_va", "permata_va",
                "other_va", "gopay", "shopeepay", "qris", "dana", "linkaja"
            ]
        }

        auth_string = base64.b64encode(f"{midtrans_server_key}:".encode()).decode()
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Basic {auth_string}'
        }

        print(f"[DEBUG] Calling Midtrans API for template order {order_id}")
        response = requests.post(snap_url, headers=headers, json=transaction_data, timeout=30, verify=True)
        print(f"[DEBUG] Response status: {response.status_code}")

        if response.status_code == 201:
            result = response.json()
            snap_token = result['token']

            try:
                conn.execute("""
                    UPDATE payments 
                    SET midtrans_transaction_id = ?, payment_response = ?
                    WHERE order_id = ?
                """, (snap_token, json.dumps(result), order_id))
                conn.commit()
                print(f"[INFO] Snap token updated for template order {order_id}")
            except Exception as e:
                print(f"[ERROR] Failed to update Snap token for template order {order_id}: {e}")
            finally:
                conn.close()

            return render_template('payment.html',
                                   snap_token=snap_token,
                                   client_key=midtrans_client_key,
                                   order_id=order_id,
                                   amount=amount,
                                   subscription_type=f'Template: {template["name"]}',
                                   template=template,
                                   is_production=is_production)
        else:
            try:
                error_response = response.json()
                error_details = error_response.get('error_messages', ['Unknown error'])
            except:
                error_details = [response.text]
            print(f"[ERROR] Midtrans API Error {response.status_code}: {error_details}")

            payment_link = "https://app.sandbox.midtrans.com/payment-links/1757060504527"
            return render_template('payment.html',
                                   snap_token=None,
                                   client_key=midtrans_client_key,
                                   order_id=order_id,
                                   amount=amount,
                                   subscription_type=f'Template: {template["name"]}',
                                   template=template,
                                   payment_link=payment_link,
                                   is_production=is_production)

    except requests.Timeout:
        print("[ERROR] Request timeout")
        flash('Koneksi ke sistem pembayaran timeout. Silakan coba lagi.', 'error')
        return redirect(url_for('buy_template', template_id=template_id))
    except requests.ConnectionError:
        print("[ERROR] Connection error")
        flash('Tidak dapat terhubung ke sistem pembayaran. Periksa koneksi internet Anda.', 'error')
        return redirect(url_for('buy_template', template_id=template_id))
    except requests.RequestException as e:
        print(f"[ERROR] Request failed: {str(e)}")
        flash('Koneksi ke sistem pembayaran gagal. Silakan coba lagi.', 'error')
        return redirect(url_for('buy_template', template_id=template_id))
    except Exception as e:
        print(f"[ERROR] Unexpected error: {str(e)}")
        flash(f'Terjadi kesalahan sistem: {str(e)}', 'error')
        return redirect(url_for('buy_template', template_id=template_id))


@app.route('/create-payment', methods=['POST'])
@require_auth
def create_payment():
    """Create payment for premium subscription using Midtrans Snap API."""
    import requests
    import json
    import base64
    from datetime import datetime

    subscription_type = request.form.get('subscription_type', 'monthly')
    template_id = request.form.get('template_id', None)  # ambil dari form
    user_id = session['user_id']

    # New simplified pricing for lifetime plans
    prices = {
        'basic': 35000,      # 2 invitations max
        'medium': 50000,     # 5 invitations max  
        'premium': 100000,   # 10 invitations max
        # Legacy mapping for backward compatibility
        'monthly': 35000,
        'quarterly': 50000,
        'yearly': 100000
    }
    gross_amount = prices.get(subscription_type, 35000)
    order_id = f"PREMIUM-{user_id}-{int(datetime.now().timestamp())}"

    try:
        # Ambil data user
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        if not user:
            flash('User tidak ditemukan!', 'error')
            return redirect(url_for('premium_page'))

        # Simpan data payment awal dengan payment_type yang benar
        try:
            conn.execute("""
                INSERT INTO payments (order_id, user_id, template_id, payment_type, status, amount, created_at)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            """, (
                order_id,
                user_id,
                template_id,
                subscription_type,  # Simpan jenis langganan
                'pending',
                gross_amount
            ))
            conn.commit()
            print(f"[INFO] Payment record inserted for order {order_id}")
        except Exception as e:
            print(f"[ERROR] Failed to insert payment record for order {order_id}: {e}")

        # Midtrans configuration
        midtrans_server_key = os.getenv("MIDTRANS_SERVER_KEY")
        midtrans_client_key = os.getenv("MIDTRANS_CLIENT_KEY")
        is_production = False
        snap_url = 'https://app.sandbox.midtrans.com/snap/v1/transactions'

        transaction_data = {
            "transaction_details": {"order_id": order_id, "gross_amount": gross_amount},
            "customer_details": {"first_name": user['name'], "email": user['email'], "phone": "081234567890"},
            "item_details": [{
                "id": f"premium-{subscription_type}",
                "price": gross_amount,
                "quantity": 1,
                "name": f"Premium Subscription ({subscription_type.title()})"
            }],
            "callbacks": {
                "finish": f"{request.url_root}payment/finish?order_id={order_id}",
                "unfinish": f"{request.url_root}payment/unfinish?order_id={order_id}",
                "error": f"{request.url_root}payment/error?order_id={order_id}"
            },
            "enabled_payments": [
                "credit_card", "bca_va", "bni_va", "bri_va", "permata_va",
                "other_va", "gopay", "shopeepay", "qris", "dana", "linkaja"
            ]
        }

        auth_string = base64.b64encode(f"{midtrans_server_key}:".encode()).decode()
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Basic {auth_string}'}

        response = requests.post(snap_url, headers=headers, json=transaction_data, timeout=30)

        if response.status_code == 201:
            result = response.json()
            snap_token = result['token']

            try:
                conn.execute('''
                    UPDATE payments 
                    SET midtrans_transaction_id = ?, payment_response = ?
                    WHERE order_id = ?
                ''', (snap_token, json.dumps(result), order_id))
                conn.commit()
                print(f"[INFO] Snap token updated for order {order_id}")
            except Exception as e:
                print(f"[ERROR] Failed to update payment with Snap token for order {order_id}: {e}")
            finally:
                conn.close()

            return render_template('payment.html', snap_token=snap_token,
                                   client_key=midtrans_client_key,
                                   order_id=order_id, amount=gross_amount,
                                   subscription_type=subscription_type,
                                   is_production=is_production)
        else:
            try:
                error_response = response.json()
                error_details = error_response.get('error_messages', ['Unknown error'])
            except:
                error_details = [response.text]
            print(f"[ERROR] Midtrans API Error {response.status_code}: {error_details}")

            payment_link = "https://app.sandbox.midtrans.com/payment-links/1757060504527"
            return render_template('payment.html', snap_token=None, client_key=midtrans_client_key,
                                   order_id=order_id, amount=gross_amount,
                                   subscription_type=subscription_type,
                                   payment_link=payment_link, is_production=is_production)

    except requests.Timeout:
        flash('Koneksi ke sistem pembayaran timeout. Silakan coba lagi.', 'error')
        return redirect(url_for('premium_page'))
    except requests.ConnectionError:
        flash('Tidak dapat terhubung ke sistem pembayaran. Periksa koneksi internet Anda.', 'error')
        return redirect(url_for('premium_page'))
    except requests.RequestException as e:
        flash(f'Koneksi ke sistem pembayaran gagal: {str(e)}', 'error')
        return redirect(url_for('premium_page'))
    except Exception as e:
        flash(f'Terjadi kesalahan sistem: {str(e)}', 'error')
        return redirect(url_for('premium_page'))


@app.route('/payment-notification', methods=['POST'])
def payment_notification():
    """Handle Midtrans payment notification"""
    import json
    import hashlib

    data = request.get_json()

    if not data:
        return jsonify({'status': 'error', 'message': 'No data received'}), 400

    order_id = data.get('order_id')
    status_code = data.get('status_code')
    gross_amount = data.get('gross_amount')
    signature_key = data.get('signature_key')

    # Verify signature
    server_key = os.getenv('MIDTRANS_SERVER_KEY', 'SB-Mid-server-YOUR_SERVER_KEY')
    expected_signature = hashlib.sha512(f"{order_id}{status_code}{gross_amount}{server_key}".encode()).hexdigest()

    if signature_key != expected_signature:
        return jsonify({'status': 'error', 'message': 'Invalid signature'}), 400

    # Update payment status
    conn = get_db()
    payment = conn.execute('SELECT * FROM payments WHERE order_id = ?', (order_id, )).fetchone()

    if payment:
        transaction_status = data.get('transaction_status')
        payment_type = data.get('payment_type')

        # Update payment record
        conn.execute('''
            UPDATE payments 
            SET status = ?, payment_method = ?, payment_response = ?, updated_at = CURRENT_TIMESTAMP
            WHERE order_id = ?
        ''', (transaction_status, payment_type, json.dumps(data), order_id))

        # If payment successful, verify user email first before granting access
        if transaction_status == 'settlement' or transaction_status == 'capture':
            # Get user info to check if email is verified
            user_info = conn.execute('SELECT email, email_verified FROM users WHERE id = ?', (payment['user_id'],)).fetchone()
            
            if not user_info or not user_info.get('email_verified'):
                # Mark payment as pending verification
                conn.execute('''
                    UPDATE payments 
                    SET status = 'pending_verification', notes = 'Waiting for email verification'
                    WHERE order_id = ?
                ''', (order_id,))
                print(f"Payment {order_id} marked as pending verification - user email not verified")
                
                # Send email verification if needed (implement email function here)
                # send_verification_email(user_info['email'], payment['user_id'], order_id)
                
            else:
                # Email verified, proceed with granting access
                if payment['payment_type'].startswith('template_'):
                    # Individual template purchase - grant template access
                    template_id = payment['payment_type'].replace('template_', '')
                    grant_template_access(payment['user_id'], template_id, payment['id'])
                else:
                    # Premium subscription
                    activate_premium_subscription(payment['user_id'], payment['payment_type'], payment['id'])

        conn.commit()

    conn.close()

    return jsonify({'status': 'success'})


@app.route('/payment-link-handler')
def payment_link_handler():
    """Handle external payment links from Midtrans"""
    payment_link_id = request.args.get('id')
    order_id = request.args.get('order_id')

    if payment_link_id:
        try:
            # Try to find the payment in our database
            conn = get_db()
            payment = None

            if order_id:
                payment = conn.execute('SELECT * FROM payments WHERE order_id = ?', (order_id,)).fetchone()

            conn.close()

            if payment:
                # Redirect to our payment success page
                return redirect(url_for('payment_success', order_id=payment['order_id']))
            else:
                # Show payment link info
                return render_template_string("""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Payment Link - Fajar Mandiri Store</title>
                    <meta charset="utf-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                </head>
                <body>
                    <div class="container mt-5">
                        <div class="row justify-content-center">
                            <div class="col-md-6">
                                <div class="card">
                                    <div class="card-body text-center">
                                        <h4 class="card-title">Payment Link</h4>
                                        <p>Payment ID: {{ payment_id }}</p>
                                        <p>Silakan gunakan link pembayaran ini untuk menyelesaikan transaksi Anda.</p>
                                        <a href="https://app.midtrans.com/payment-links/{{ payment_id }}" 
                                           class="btn btn-primary" target="_blank">
                                            Buka Link Pembayaran
                                        </a>
                                        <hr>
                                        <a href="{{ url_for('premium_page') }}" class="btn btn-secondary">
                                            Kembali ke Premium Page
                                        </a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </body>
                </html>
                """, payment_id=payment_link_id)

        except Exception as e:
            print(f"Error handling payment link: {e}")
            flash('Terjadi kesalahan saat memproses payment link.', 'error')
            return redirect(url_for('premium_page'))

    flash('Payment link tidak valid.', 'error')
    return redirect(url_for('premium_page'))


@app.route('/payment-success')
def payment_success():
    """Payment success page"""
    order_id = request.args.get('order_id')
    return render_template('payment_success.html', order_id=order_id)


@app.route('/payment/unfinish')
def payment_unfinish():
    """Midtrans unfinish redirect URL - when payment is cancelled or incomplete"""
    order_id = request.args.get('order_id', '')

    print(f"Payment unfinish - Order: {order_id}")
    flash('Pembayaran dibatalkan atau belum selesai. Anda dapat mencoba lagi kapan saja.', 'warning')

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Pembayaran Belum Selesai - Fajar Mandiri Store</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-body text-center">
                            <div class="mb-4">
                                <i class="fas fa-exclamation-triangle text-warning" style="font-size: 4rem;"></i>
                            </div>
                            <h4 class="card-title">Pembayaran Belum Selesai</h4>
                            <p class="card-text">
                                Pembayaran Anda belum diselesaikan atau dibatalkan.
                                {% if order_id %}
                                <br><small class="text-muted">Order ID: {{ order_id }}</small>
                                {% endif %}
                            </p>
                            <div class="mt-4">
                                <a href="{{ url_for('create_wedding_invitation') }}" class="btn btn-primary">Coba Lagi</a>
                                <a href="{{ url_for('index') }}" class="btn btn-secondary">Kembali ke Beranda</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <script src="https://kit.fontawesome.com/your-fontawesome-kit.js"></script>
    </body>
    </html>
    """, order_id=order_id)


@app.route('/payment/error')
def payment_error():
    """Midtrans error redirect URL - when payment encounters an error"""
    order_id = request.args.get('order_id', '')

    print(f"Payment error - Order: {order_id}")
    flash('Terjadi kesalahan dalam proses pembayaran. Silakan coba lagi.', 'danger')

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Error Pembayaran - Fajar Mandiri Store</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-body text-center">
                            <div class="mb-4">
                                <i class="fas fa-times-circle text-danger" style="font-size: 4rem;"></i>
                            </div>
                            <h4 class="card-title">Error Pembayaran</h4>
                            <p class="card-text">
                                Maaf, terjadi kesalahan dalam proses pembayaran.
                                {% if order_id %}
                                <br><small class="text-muted">Order ID: {{ order_id }}</small>
                                {% endif %}
                            </p>
                            <div class="mt-4">
                                <a href="{{ url_for('create_wedding_invitation') }}" class="btn btn-primary">Coba Lagi</a>
                                <a href="{{ url_for('contact') }}" class="btn btn-warning">Hubungi Customer Service</a>
                                <a href="{{ url_for('index') }}" class="btn btn-secondary">Kembali ke Beranda</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <script src="https://kit.fontawesome.com/your-fontawesome-kit.js"></script>
    </body>
    </html>
    """, order_id=order_id)


@app.route('/notification/handling', methods=['POST'])
def notification_handling():
    """Enhanced Midtrans notification handler with accurate status processing"""
    import json
    import hashlib
    import time

    try:
        # Get JSON data from Midtrans
        data = request.get_json() or {}

        # Log the notification
        print(f"PAYMENT_NOTIFICATION: Received data: {json.dumps(data, indent=2)}")

        # Extract key information
        order_id = data.get('order_id')
        status_code = data.get('status_code') 
        gross_amount = data.get('gross_amount')
        signature_key = data.get('signature_key')
        transaction_status = data.get('transaction_status')
        fraud_status = data.get('fraud_status')
        transaction_id = data.get('transaction_id')
        payment_type = data.get('payment_type')

        if not order_id:
            print("PAYMENT_ERROR: No order_id in notification")
            return jsonify({'status': 'error', 'message': 'No order_id'}), 400

        # Enhanced signature verification
        server_key = os.getenv('MIDTRANS_SERVER_KEY', '')
        if server_key and signature_key:
            signature_params = f"{order_id}{status_code}{gross_amount}{server_key}"
            expected_signature = hashlib.sha512(signature_params.encode()).hexdigest()

            if signature_key != expected_signature:
                print(f"PAYMENT_SECURITY: Invalid signature for order {order_id}")
                return jsonify({'status': 'error', 'message': 'Invalid signature'}), 401

        # Update payment status in database without locks for faster webhook response
        conn = get_db()
        conn.execute('PRAGMA busy_timeout = 30000')  # 30 second timeout instead of immediate lock

        try:
            # Get current payment record
            payment = conn.execute(
                'SELECT * FROM payments WHERE order_id = ?', 
                (order_id,)
            ).fetchone()

            if not payment:
                print(f"PAYMENT_ERROR: Payment record not found for order {order_id}")
                conn.rollback()
                conn.close()
                return jsonify({'status': 'error', 'message': 'Payment record not found'}), 404

            # Determine final status based on Midtrans response
            final_status = transaction_status

            # Handle settlement and capture as success
            if transaction_status == 'settlement' or (transaction_status == 'capture' and fraud_status == 'accept'):
                final_status = 'settlement'
                print(f"PAYMENT_SUCCESS: Order {order_id} confirmed as SETTLEMENT")

                # Grant access immediately for successful payments
                if order_id.startswith('TEMPLATE-'):
                    parts = order_id.split('-')
                    if len(parts) >= 3:
                        template_id = parts[1]
                        user_id = parts[2]

                        print(f"PAYMENT_GRANT: Processing template access - User: {user_id}, Template: {template_id}")

                        # Grant template access immediately - no retry needed with better function
                        print(f"PAYMENT_GRANT: Processing template access - User: {user_id}, Template: {template_id}")
                        access_granted = grant_template_access(user_id, template_id, payment['id'])
                        if access_granted:
                            print(f"PAYMENT_SUCCESS: Template access granted for user {user_id}, template {template_id}")
                        else:
                            print(f"PAYMENT_WARNING: Could not grant template access automatically, will be available via payment finish")

                elif order_id.startswith('PREMIUM-'):
                    parts = order_id.split('-')
                    if len(parts) >= 2:
                        user_id = parts[1]
                        subscription_type = payment['payment_type'] if payment and payment.get('payment_type') else 'monthly'
                        print(f"PREMIUM_ACTIVATE: Activating {subscription_type} subscription for user {user_id}")
                        activate_success = activate_premium_subscription(user_id, subscription_type, payment['id'])
                        if activate_success:
                            print(f"PREMIUM_SUCCESS: Premium subscription activated for user {user_id}")
                        else:
                            print(f"PREMIUM_ERROR: Failed to activate subscription for user {user_id}")

            elif transaction_status in ['deny', 'cancel', 'expire', 'failure']:
                final_status = 'failed'
                print(f"PAYMENT_FAILED: Order {order_id} marked as FAILED - Status: {transaction_status}")

            elif transaction_status == 'pending':
                final_status = 'pending'
                print(f"PAYMENT_PENDING: Order {order_id} still PENDING")

            # Update payment status
            conn.execute('''
                UPDATE payments 
                SET status = ?, 
                    midtrans_transaction_id = ?,
                    payment_response = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE order_id = ?
            ''', (final_status, transaction_id, json.dumps(data), order_id))

            conn.commit()
            print(f"PAYMENT_UPDATE: Order {order_id} status updated to {final_status}")

        except Exception as e:
            conn.rollback()
            print(f"PAYMENT_ERROR: Transaction rollback for order {order_id}: {str(e)}")
            raise e
        finally:
            conn.close()

        return jsonify({'status': 'success', 'order_id': order_id, 'final_status': final_status})

    except Exception as e:
        print(f"PAYMENT_CRITICAL: Error processing notification: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Add an alternative endpoint that redirects to the main notification handler
@app.route('/payment-notification-alt', methods=['POST'])
def payment_notification_alt():
    """Alternative endpoint for Midtrans payment notifications."""
    # Redirect to the main notification handler
    return notification_handling()


@app.route('/payment/finish')
def payment_finish():
    """Midtrans finish redirect URL - immediately grant access and redirect to template usage"""
    order_id = request.args.get('order_id')
    status_code = request.args.get('status_code')
    transaction_status = request.args.get('transaction_status')

    print(f"Payment finish - Order: {order_id}, Status: {transaction_status}")

    if transaction_status in ['settlement', 'capture'] or not transaction_status:
        # Check if this is a template purchase
        if order_id and order_id.startswith('TEMPLATE-'):
            try:
                # Extract template_id from order_id format: TEMPLATE-{template_id}-{user_id}-{timestamp}
                parts = order_id.split('-')
                if len(parts) >= 3:
                    template_id = parts[1]
                    user_id = parts[2]

                    # Verify user session matches
                    if 'user_id' in session and str(session['user_id']) == str(user_id):
                        # Grant template access using the improved function
                        conn = get_db()
                        payment = conn.execute('SELECT * FROM payments WHERE order_id = ?', (order_id,)).fetchone()
                        conn.close()

                        if payment:
                            access_granted = grant_template_access(user_id, template_id, payment['id'])
                            
                            if access_granted:
                                flash('🎉 Pembayaran berhasil! Template premium telah aktif dan siap digunakan.', 'success')
                                # Redirect directly to create invitation with template selected
                                return redirect(url_for('create_wedding_invitation') + f'?template_id={template_id}&payment_success=1')
                            else:
                                flash('⚠️ Pembayaran berhasil, tetapi ada masalah mengaktifkan template. Silakan hubungi support.', 'warning')
                    else:
                        flash('⚠️ Session tidak valid. Silakan login ulang.', 'error')
                        return redirect(url_for('login'))
                        
            except Exception as e:
                print(f"Error processing template payment finish: {e}")
                flash('⚠️ Ada masalah memproses pembayaran. Silakan hubungi support.', 'error')
        
        # Check if this is a premium subscription purchase
        elif order_id and order_id.startswith('PREMIUM-'):
            try:
                parts = order_id.split('-')
                if len(parts) >= 2:
                    user_id = parts[1]
                    
                    # Verify user session matches
                    if 'user_id' in session and str(session['user_id']) == str(user_id):
                        conn = get_db()
                        payment = conn.execute('SELECT * FROM payments WHERE order_id = ?', (order_id,)).fetchone()
                        conn.close()
                        
                        if payment:
                            subscription_type = payment['payment_type'] if payment.get('payment_type') else 'monthly'
                            success = activate_premium_subscription(user_id, subscription_type, payment['id'])
                            
                            if success:
                                flash('🎉 Langganan Premium berhasil diaktifkan! Sekarang Anda dapat menggunakan semua template.', 'success')
                                return redirect(url_for('create_wedding_invitation') + '?premium_activated=1')
                            else:
                                flash('⚠️ Pembayaran berhasil, tetapi ada masalah mengaktifkan langganan. Silakan hubungi support.', 'warning')
                    else:
                        flash('⚠️ Session tidak valid. Silakan login ulang.', 'error')
                        return redirect(url_for('login'))
                        
            except Exception as e:
                print(f"Error processing premium payment finish: {e}")
                flash('⚠️ Ada masalah memproses pembayaran langganan. Silakan hubungi support.', 'error')

        flash('✅ Pembayaran berhasil! Terima kasih atas pembelian Anda.', 'success')
    elif transaction_status == 'pending':
        flash('⏳ Pembayaran sedang diproses. Mohon tunggu konfirmasi.', 'info')
    else:
        flash(f'Status pembayaran: {transaction_status}', 'info')

    return redirect(url_for('payment_success') + f'?order_id={order_id}')


def grant_template_access(user_id, template_id, payment_id):
    """Enhanced grant template access with better connection management and reduced locking time"""
    import sqlite3
    import time
    max_retries = 3
    retry_delay = 0.1
    
    for attempt in range(max_retries):
        conn = None
        try:
            conn = get_db()
            conn.execute('PRAGMA busy_timeout = 5000')  # 5 second timeout
            
            # Quick check if access already exists (without transaction)
            existing_access = conn.execute('''
                SELECT id FROM template_access 
                WHERE user_id = ? AND template_id = ? AND template_type = ? AND is_active = 1
            ''', (user_id, template_id, 'wedding')).fetchone()

            if existing_access:
                print(f"ACCESS_EXISTS: User {user_id} already has access to template {template_id}")
                conn.close()
                return True

            # Start transaction only when needed
            conn.execute('BEGIN IMMEDIATE')
            
            try:
                # Insert new active access record (use INSERT OR IGNORE to handle race conditions)
                cursor = conn.execute('''
                    INSERT OR IGNORE INTO template_access 
                    (user_id, template_id, template_type, payment_id, is_active, granted_at, created_at)
                    VALUES (?, ?, ?, ?, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ''', (user_id, template_id, 'wedding', payment_id))

                if cursor.rowcount > 0:
                    new_access_id = cursor.lastrowid
                    print(f"ACCESS_GRANTED: Created access record ID {new_access_id} for user {user_id}, template {template_id}, payment {payment_id}")
                else:
                    # Record might already exist, check again
                    existing = conn.execute('''
                        SELECT id FROM template_access 
                        WHERE user_id = ? AND template_id = ? AND template_type = ? AND is_active = 1
                    ''', (user_id, template_id, 'wedding')).fetchone()
                    
                    if existing:
                        print(f"ACCESS_EXISTS_RACE: User {user_id} already has access to template {template_id} (race condition)")
                        conn.commit()
                        conn.close()
                        return True

                conn.commit()
                print(f"ACCESS_SUCCESS: Template access verified and committed for user {user_id}, template {template_id}")
                
                # Quick final verification
                final_check = conn.execute('''
                    SELECT COUNT(*) as count FROM template_access 
                    WHERE user_id = ? AND template_id = ? AND template_type = ? AND is_active = 1
                ''', (user_id, template_id, 'wedding')).fetchone()

                conn.close()

                if final_check and final_check['count'] > 0:
                    print(f"ACCESS_VERIFIED: Final verification successful for user {user_id}, template {template_id}")
                    return True
                else:
                    print(f"ACCESS_ERROR: Final verification failed for user {user_id}, template {template_id}")
                    return False

            except Exception as transaction_error:
                conn.rollback()
                raise transaction_error

        except sqlite3.OperationalError as e:
            if "database is locked" in str(e) and attempt < max_retries - 1:
                print(f"PAYMENT_RETRY {attempt + 1}/{max_retries}: Database locked, retrying...")
                if conn:
                    try:
                        conn.close()
                    except:
                        pass
                import time
                time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                continue
            else:
                print(f"ACCESS_CRITICAL: Database locked error after {attempt + 1} attempts for user {user_id}, template {template_id}: {str(e)}")
                if conn:
                    try:
                        conn.close()
                    except:
                        pass
                return False
        except Exception as e:
            print(f"ACCESS_ERROR: Error in attempt {attempt + 1} for user {user_id}, template {template_id}: {str(e)}")
            if conn:
                try:
                    conn.rollback()
                    conn.close()
                except:
                    pass
            if attempt == max_retries - 1:
                return False
            import time
            time.sleep(retry_delay)
    
    print(f"PAYMENT_CRITICAL: Failed to grant template access after {max_retries} attempts")
    return False



@app.route('/fix-template-access/<order_id>')
@require_auth
def fix_template_access(order_id):
    """Manual fix for template access when payment succeeded but access wasn't granted"""
    try:
        if order_id.startswith('TEMPLATE-'):
            parts = order_id.split('-')
            if len(parts) >= 3:
                template_id = parts[1]
                user_id = parts[2]

                # Check if payment was successful
                conn = get_db()
                payment = conn.execute('''
                    SELECT * FROM payments 
                    WHERE order_id = ? AND status = 'settlement'
                ''', (order_id,)).fetchone()

                if payment and str(payment['user_id']) == str(session['user_id']):
                    # Grant access manually
                    success = grant_template_access(user_id, template_id, payment['id'])
                    if success:
                        flash('✅ Template access berhasil diperbaiki!', 'success')
                        return redirect(url_for('create_wedding_invitation') + f'?template_id={template_id}&payment_success=1')
                    else:
                        flash('❌ Gagal memperbaiki akses template!', 'error')
                else:
                    flash('❌ Pembayaran tidak ditemukan atau belum berhasil!', 'error')

                conn.close()

        flash('❌ Order ID tidak valid!', 'error')
        return redirect(url_for('dashboard'))

    except Exception as e:
        print(f"Error fixing template access: {e}")
        flash('❌ Terjadi kesalahan sistem!', 'error')
        return redirect(url_for('dashboard'))


@app.route('/fix-all-template-access')
@require_auth
def fix_all_template_access():
    """Fix all template access for current user based on successful payments"""
    try:
        user_id = session['user_id']
        conn = get_db()

        # Find all successful template payments for this user
        successful_payments = conn.execute('''
            SELECT * FROM payments 
            WHERE user_id = ? AND status = 'settlement' 
            AND order_id LIKE 'TEMPLATE-%'
            ORDER BY created_at DESC
        ''', (user_id,)).fetchall()

        fixed_count = 0
        total_payments = len(successful_payments)
        template_names = []

        print(f"DEBUG: Found {total_payments} successful payments for user {user_id}")

        for payment in successful_payments:
            try:
                order_id = payment['order_id']
                print(f"DEBUG: Processing payment {order_id}")

                if order_id.startswith('TEMPLATE-'):
                    parts = order_id.split('-')
                    if len(parts) >= 3:
                        template_id = parts[1]

                        # Get template name for feedback
                        template_info = conn.execute('''
                            SELECT name FROM wedding_templates WHERE id = ?
                        ''', (template_id,)).fetchone()

                        template_name = template_info['name'] if template_info else f"Template {template_id}"

                        # Check if access already exists and is active
                        existing_access = conn.execute('''
                            SELECT COUNT(*) as count FROM template_access 
                            WHERE user_id = ? AND template_id = ? AND template_type = 'wedding' AND is_active = 1
                        ''', (user_id, template_id)).fetchone()

                        current_access_count = existing_access['count'] if existing_access else 0
                        print(f"DEBUG: Template {template_id} current access count: {current_access_count}")

                        if current_access_count == 0:
                            # Grant access
                            print(f"DEBUG: Granting access for template {template_id}")
                            success = grant_template_access(user_id, template_id, payment['id'])
                            if success:
                                fixed_count += 1
                                template_names.append(template_name)
                                print(f"SUCCESS: Fixed access for template {template_id} ({template_name}) from payment {order_id}")
                            else:
                                print(f"FAILED: Could not grant access for template {template_id}")
                        else:
                            print(f"DEBUG: Template {template_id} already has access, skipping")

            except Exception as e:
                print(f"Error processing payment {payment.get('order_id', 'unknown')}: {e}")
                import traceback
                traceback.print_exc()
                continue

        conn.close()

        if fixed_count > 0:
            template_list = ', '.join(template_names[:3])  # Show first 3 template names
            if len(template_names) > 3:
                template_list += f" dan {len(template_names) - 3} lainnya"

            flash(f'✅ Berhasil memperbaiki akses untuk {fixed_count} template: {template_list}!', 'success')
        else:
            flash(f'ℹ️ Tidak ada template yang perlu diperbaiki. Semua akses sudah benar dari {total_payments} pembayaran.', 'info')

        return redirect(url_for('create_wedding_invitation'))

    except Exception as e:
        print(f"Error fixing all template access: {e}")
        import traceback
        traceback.print_exc()
        flash('❌ Terjadi kesalahan sistem!', 'error')
        return redirect(url_for('dashboard'))


@app.route('/admin/payment-debug')
@require_admin
def admin_payment_debug():
    """Debug payment system for admin"""
    conn = get_db()

    # Get recent payments
    recent_payments = conn.execute('''
        SELECT p.*, u.name as user_name, u.email as user_email
        FROM payments p
        LEFT JOIN users u ON p.user_id = u.id
        ORDER BY p.created_at DESC
        LIMIT 20
    ''').fetchall()

    # Get payment statistics
    payment_stats = {
        'total_payments': conn.execute('SELECT COUNT(*) FROM payments').fetchone()[0],
        'pending_payments': conn.execute('SELECT COUNT(*) FROM payments WHERE status = "pending"').fetchone()[0],
        'successful_payments': conn.execute('SELECT COUNT(*) FROM payments WHERE status = "settlement"').fetchone()[0],
        'failed_payments': conn.execute('SELECT COUNT(*) FROM payments WHERE status IN ("deny", "cancel", "expire", "failure")').fetchone()[0]
    }

    conn.close()

    # Environment info
    env_info = {
        'midtrans_server_key': os.getenv('MIDTRANS_SERVER_KEY', 'Not set')[:20] + '...',
        'midtrans_client_key': os.getenv('MIDTRANS_CLIENT_KEY', 'Not set')[:20] + '...',
        'is_production': not os.getenv('MIDTRANS_SERVER_KEY', '').startswith('SB-'),
        'base_url': request.url_root
    }

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Debug - Admin</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-4">
            <h2>Payment System Debug</h2>

            <div class="row">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5>Environment Info</h5>
                        </div>
                        <div class="card-body">
                            {% for key, value in env_info.items() %}
                            <p><strong>{{ key }}:</strong> {{ value }}</p>
                            {% endfor %}
                        </div>
                    </div>
                </div>

                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5>Payment Statistics</h5>
                        </div>
                        <div class="card-body">
                            {% for key, value in payment_stats.items() %}
                            <p><strong>{{ key.replace('_', ' ').title() }}:</strong> {{ value }}</p>
                            {% endfor %}
                        </div>
                    </div>
                </div>
            </div>

            <div class="card mt-4">
                <div class="card-header">
                    <h5>Recent Payments</h5>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>Order ID</th>
                                    <th>User</th>
                                    <th>Amount</th>
                                    <th>Type</th>
                                    <th>Status</th>
                                    <th>Created</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for payment in recent_payments %}
                                <tr>
                                    <td>{{ payment.order_id }}</td>
                                    <td>{{ payment.user_name or 'Unknown' }}</td>
                                    <td>Rp {{ "{:,}".format(payment.amount).replace(",", ".") }}</td>
                                    <td>{{ payment.payment_type }}</td>
                                    <td>
                                        <span class="badge 
                                            {% if payment.status == 'settlement' %}bg-success
                                            {% elif payment.status == 'pending' %}bg-warning
                                            {% else %}bg-danger{% endif %}">
                                            {{ payment.status }}
                                        </span>
                                    </td>
                                    <td>{{ payment.created_at }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div class="mt-3">
                <a href="{{ url_for('admin_dashboard') }}" class="btn btn-secondary">Back to Dashboard</a>
            </div>
        </div>
    </body>
    </html>
    """, env_info=env_info, payment_stats=payment_stats, recent_payments=recent_payments)


def activate_premium_subscription(user_id, subscription_type, payment_id):
    """Activate new subscription plans with database-level access control"""
    from datetime import datetime, timedelta
    
    try:
        # New subscription plans - no time limits, only usage limits
        plan_config = {
            'basic': {
                'plan_name': 'basic',
                'plan_price': 35000,
                'invitation_limit': 2,
                'cv_limit': -1,  # unlimited
                'has_premium_templates': True,
                'end_date': None  # no expiry
            },
            'medium': {
                'plan_name': 'medium', 
                'plan_price': 50000,
                'invitation_limit': 5,
                'cv_limit': -1,  # unlimited
                'has_premium_templates': True,
                'end_date': None  # no expiry
            },
            'premium': {
                'plan_name': 'premium',
                'plan_price': 100000,
                'invitation_limit': 10,
                'cv_limit': -1,  # unlimited
                'has_premium_templates': True,
                'end_date': None  # no expiry
            }
        }

        # Map old subscription types to new plans
        type_to_plan = {
            'monthly': 'basic',
            'quarterly': 'medium', 
            'yearly': 'premium',
            'basic': 'basic',
            'medium': 'medium',
            'premium': 'premium'
        }

        plan_key = type_to_plan.get(subscription_type, 'basic')
        config = plan_config[plan_key]
        
        print(f"SUBSCRIPTION_ACTIVATE: Activating {config['plan_name']} plan for user {user_id}")

        # Use simple connection without immediate locks
        conn = get_db()
        conn.execute('PRAGMA busy_timeout = 30000')  # 30 second timeout instead of immediate lock
        
        try:
            # Deactivate existing subscriptions without transaction lock
            conn.execute('UPDATE premium_subscriptions SET is_active = 0 WHERE user_id = ?', (user_id,))

            # Create new subscription record
            conn.execute('''
                INSERT INTO premium_subscriptions (
                    user_id, payment_id, subscription_type, plan_name, plan_price, 
                    invitation_limit, cv_limit, has_premium_templates, end_date, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, payment_id, subscription_type, config['plan_name'], 
                  config['plan_price'], config['invitation_limit'], config['cv_limit'],
                  config['has_premium_templates'], config['end_date'], 1))

            # Update user with new plan limits
            conn.execute('''
                UPDATE users SET 
                    is_premium = 1, 
                    current_plan = ?, 
                    invitation_limit = ?,
                    cv_limit = ?,
                    premium_expires_at = ? 
                WHERE id = ?
            ''', (config['plan_name'], config['invitation_limit'], 
                  config['cv_limit'], config['end_date'], user_id))

            conn.commit()
            print(f"SUBSCRIPTION_SUCCESS: {config['plan_name']} plan activated for user {user_id}")
            conn.close()
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"SUBSCRIPTION_ERROR: Database error activating plan for user {user_id}: {e}")
            conn.close()
            return False
            
    except Exception as e:
        print(f"SUBSCRIPTION_CRITICAL: Critical error activating plan for user {user_id}: {e}")
        return False


@app.route('/admin/wedding-invitations')
@require_admin
def admin_wedding_invitations():
    conn = get_db()
    invitations = conn.execute('''
        SELECT wi.*, u.name as user_name, u.email as user_email,
               COUNT(wg.id) as guest_count
        FROM wedding_invitations wi
        LEFT JOIN users u ON wi.user_id = u.id
        LEFT JOIN wedding_guests wg ON wi.id = wg.invitation_id
        GROUP BY wi.id
        ORDER BY wi.created_at DESC
    ''').fetchall()
    conn.close()

    return render_template('admin/wedding_invitations.html',
                           invitations=invitations)


@app.route('/admin/edit-invitation/<int:invitation_id>',
           methods=['GET', 'POST'])
@require_admin
def admin_edit_invitation(invitation_id):
    conn = get_db()
    invitation = conn.execute('SELECT * FROM wedding_invitations WHERE id = ?',
                              (invitation_id, )).fetchone()

    if not invitation:
        flash('Undangan tidak ditemukan!', 'error')
        return redirect(url_for('admin_wedding_invitations'))

    if request.method == 'POST':
        # Update invitation data
        bride_name = request.form['bride_name']
        bride_title = request.form.get('bride_title', '')
        bride_father = request.form['bride_father']
        bride_mother = request.form['bride_mother']
        groom_name = request.form['groom_name']
        groom_title = request.form.get('groom_title', '')
        groom_father = request.form['groom_father']
        groom_mother = request.form['groom_mother']

        couple_name = f"{bride_name} & {groom_name}"
        template_id = int(
            request.form.get('template_id', invitation['template_id']))
        custom_message = request.form.get('custom_message', '')
        guest_limit = int(request.form.get('guest_limit', 100))

        # Event handling
        event_type = request.form.get('event_type', 'single')

        wedding_date = request.form.get('wedding_date', '')
        wedding_time = request.form.get('wedding_time', '')
        venue_name = request.form.get('venue_name', '')
        venue_address = request.form.get('venue_address', '')

        akad_date = request.form.get('akad_date', '')
        akad_time = request.form.get('akad_time', '')
        akad_venue_name = request.form.get('akad_venue_name', '')
        akad_venue_address = request.form.get('akad_venue_address', '')

        resepsi_date = request.form.get('resepsi_date', '')
        resepsi_time = request.form.get('resepsi_time', '')
        resepsi_venue_name = request.form.get('resepsi_venue_name', '')
        resepsi_venue_address = request.form.get('resepsi_venue_address', '')

        bank_name = request.form.get('bank_name', '')
        bank_account = request.form.get('bank_account', '')
        account_holder = request.form.get('account_holder', '')

        # Update to database
        conn.execute(
            '''
            UPDATE wedding_invitations SET
            couple_name = ?, bride_name = ?, bride_title = ?, bride_father = ?, bride_mother = ?,
            groom_name = ?, groom_title = ?, groom_father = ?, groom_mother = ?,
            wedding_date = ?, wedding_time = ?, venue_name = ?, venue_address = ?,
            template_id = ?, custom_message = ?, guest_limit = ?,
            akad_date = ?, akad_time = ?, akad_venue_name = ?, akad_venue_address = ?,
            resepsi_date = ?, resepsi_time = ?, resepsi_venue_name = ?, resepsi_venue_address = ?,
            bank_name = ?, bank_account = ?, account_holder = ?
            WHERE id = ?
        ''', (couple_name, bride_name, bride_title, bride_father, bride_mother,
              groom_name, groom_title, groom_father, groom_mother, wedding_date
              or None, wedding_time or None, venue_name, venue_address,
              template_id, custom_message, guest_limit, akad_date or None,
              akad_time or None, akad_venue_name or None, akad_venue_address
              or None, resepsi_date or None, resepsi_time
              or None, resepsi_venue_name or None, resepsi_venue_address
              or None, bank_name, bank_account, account_holder, invitation_id))

        conn.commit()
        conn.close()

        flash('Undangan berhasil diperbarui!', 'success')
        return redirect(url_for('admin_wedding_invitations'))

    # Get wedding templates for selection
    wedding_templates = conn.execute(
        'SELECT * FROM wedding_templates ORDER BY name').fetchall()
    conn.close()

    return render_template('admin/edit_invitation.html',
                           invitation=invitation,
                           wedding_templates=wedding_templates)


@app.route('/admin/delete-invitation/<int:invitation_id>')
@require_admin
def admin_delete_invitation(invitation_id):
    conn = get_db()
    invitation = conn.execute('SELECT * FROM wedding_invitations WHERE id = ?',
                              (invitation_id, )).fetchone()

    if not invitation:
        flash('Undangan tidak ditemukan!', 'error')
        return redirect(url_for('admin_wedding_invitations'))

    # Delete associated guests first
    conn.execute('DELETE FROM wedding_guests WHERE invitation_id = ?',
                 (invitation_id, ))
    # Delete invitation
    conn.execute('DELETE FROM wedding_invitations WHERE id = ?',
                 (invitation_id, ))
    conn.commit()
    conn.close()

    flash(f'Undangan "{invitation["couple_name"]}" berhasil dihapus!',
          'success')
    return redirect(url_for('admin_wedding_invitations'))


@app.route('/admin/toggle-invitation/<int:invitation_id>')
@require_admin
def admin_toggle_invitation(invitation_id):
    conn = get_db()
    invitation = conn.execute('SELECT * FROM wedding_invitations WHERE id = ?',
                              (invitation_id, )).fetchone()

    if not invitation:
        flash('Undangan tidak ditemukan!', 'error')
        return redirect(url_for('admin_wedding_invitations'))

    new_status = 0 if invitation['is_active'] else 1
    conn.execute('UPDATE wedding_invitations SET is_active = ? WHERE id = ?',
                 (new_status, invitation_id))
    conn.commit()
    conn.close()

    status_text = 'diaktifkan' if new_status else 'dinonaktifkan'
    flash(f'Undangan "{invitation["couple_name"]}" berhasil {status_text}!',
          'success')
    return redirect(url_for('admin_wedding_invitations'))


@app.route('/admin/orders')
@require_admin
def admin_orders():
    conn = get_db()
    orders = conn.execute('''
        SELECT o.*, u.name as user_name
        FROM orders o
        LEFT JOIN users u ON o.user_id = u.id
        ORDER BY o.created_at DESC
    ''').fetchall()
    conn.close()

    return render_template('admin/orders.html', orders=orders)


@app.route('/update-order-status', methods=['POST'])
@require_admin
def update_order_status():
    order_id = request.form['order_id']
    status = request.form['status']

    conn = get_db()
    conn.execute('UPDATE orders SET status = ? WHERE id = ?',
                 (status, order_id))
    conn.commit()
    conn.close()

    flash('Status pesanan berhasil diperbarui!', 'success')
    return redirect(request.referrer or url_for('admin_orders'))


@app.route('/view-order/<int:order_id>')
@require_admin
def view_order(order_id):
    conn = get_db()
    order = conn.execute(
        '''
        SELECT o.*, u.name as user_name
        FROM orders o
        LEFT JOIN users u ON o.user_id = u.id
        WHERE o.id = ?
    ''', (order_id, )).fetchone()
    conn.close()

    if not order:
        flash('Pesanan tidak ditemukan!', 'error')
        return redirect(url_for('admin_orders'))

    return render_template('admin/view_order.html', order=order)


@app.route('/download-file/<int:order_id>')
@require_admin
def download_file(order_id):
    conn = get_db()
    order = conn.execute('SELECT file_path FROM orders WHERE id = ?',
                         (order_id, )).fetchone()
    conn.close()

    if not order or not order['file_path']:
        flash('File tidak ditemukan!', 'error')
        return redirect(url_for('admin_orders'))

    try:
        # The file_path is relative to the configured folder (UPLOAD_FOLDER/PREWEDDING_FOLDER).
        # send_file needs the absolute path or a path relative to the script's directory if the directory is configured.
        # Since app.config['UPLOAD_FOLDER'] is already set to the correct base, we join it.
        return send_file(os.path.join(app.config['UPLOAD_FOLDER'],
                                      order['file_path']),
                         as_attachment=True)
    except FileNotFoundError:
        flash('File tidak ditemukan di server!',
              'error')  # Corrected error message
        return redirect(url_for('admin_orders'))


@app.route('/download-template/<template_type>/<filename>')
def download_template(template_type, filename):
    if template_type == 'cv':
        directory = app.config['TEMPLATES_FOLDER']
    elif template_type == 'wedding':
        directory = app.config['WEDDING_FOLDER']
    else:
        return "Invalid template type", 404

    try:
        return send_file(os.path.join(directory, filename), as_attachment=True)
    except FileNotFoundError:
        return "File not found", 404


@app.route('/reset-database')
def reset_db_route():
    """Route untuk reset database - HANYA UNTUK DEVELOPMENT"""
    if app.debug:
        reset_database()
        flash('Database berhasil direset!', 'success')
        return redirect(url_for('index'))
    else:
        return "Not allowed in production", 403


@app.route('/debug-db')
def debug_db():
    """Debug route untuk cek isi database"""
    if app.debug:
        conn = get_db()

        # Cek semua undangan
        all_invitations = conn.execute(
            'SELECT * FROM wedding_invitations').fetchall()

        # Cek user yang sedang login
        current_user_invitations = []
        if 'user_id' in session:
            current_user_invitations = conn.execute(
                'SELECT * FROM wedding_invitations WHERE user_id = ?',
                (session['user_id'], )).fetchall()

        # Cek semua template wedding
        all_templates = conn.execute(
            'SELECT id, name, template_file FROM wedding_templates').fetchall(
            )

        conn.close()

        debug_info = {
            'user_id':
            session.get('user_id', 'Not logged in'),
            'total_invitations':
            len(all_invitations),
            'user_invitations':
            len(current_user_invitations),
            'all_invitations': [dict(inv) for inv in all_invitations],
            'user_invitations_data':
            [dict(inv) for inv in current_user_invitations],
            'wedding_templates': [dict(tmpl) for tmpl in all_templates]
        }

        return f"<pre>{json.dumps(debug_info, indent=2, default=str)}</pre>"
    else:
        return "Not allowed in production", 403


@app.route('/test-create', methods=['GET', 'POST'])
def test_create():
    """Test route untuk debug create invitation"""
    if not app.debug:
        return "Not allowed in production", 403

    if request.method == 'POST':
        # Test manual insert
        try:
            conn = get_db()
            cursor = conn.execute(
                '''
                INSERT INTO wedding_invitations
                (user_id, couple_name, bride_name, bride_father, bride_mother, groom_name, groom_father, groom_mother, venue_address, template_id, invitation_link, guest_limit)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (1, 'Test Couple', 'Test Bride', 'Test Father', 'Test Mother',
                  'Test Groom', 'Test Father 2', 'Test Mother 2', 'Test Venue',
                  1, 'test-link-123', 100))

            invitation_id = cursor.lastrowid
            conn.commit()
            conn.close()

            return f"Test invitation created with ID: {invitation_id}"
        except Exception as e:
            return f"Error creating test invitation: {str(e)}"

    return '''
    <form method="POST">
        <button type="submit">Create Test Invitation</button>
    </form>
    '''


# --- fungsi database ---
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = [
        dict((cur.description[idx][0], value) for idx, value in enumerate(row))
        for row in cur.fetchall()
    ]
    cur.close()
    return (rv[0] if rv else None) if one else rv


def has_template_access(user_id, template_id, template_type='wedding'):
    """Check if user has access to specific template (premium subscription or individual purchase)"""
    try:
        conn = get_db()

        print(f"DEBUG: Checking template access - User: {user_id}, Template: {template_id}, Type: {template_type}")

        # Check if user has premium subscription and it's still valid
        user = conn.execute('SELECT is_premium, premium_expires_at FROM users WHERE id = ?', (user_id,)).fetchone()
        if user and user['is_premium']:
            print(f"DEBUG: User {user_id} has premium subscription")
            # Check if premium subscription is still valid
            if user['premium_expires_at']:
                from datetime import datetime
                try:
                    expires_at = datetime.fromisoformat(user['premium_expires_at'].replace('Z', '+00:00'))
                    if expires_at > datetime.now():
                        print(f"DEBUG: Premium subscription valid until {expires_at}")
                        conn.close()
                        return True
                    else:
                        print(f"DEBUG: Premium subscription expired on {expires_at}")
                except:
                    # Fallback for old datetime format
                    print(f"DEBUG: Premium subscription active (fallback)")
                    conn.close() 
                    return True
            else:
                # No expiry date means unlimited premium
                print(f"DEBUG: Premium subscription unlimited")
                conn.close() 
                return True

        # Check if user has individual template access
        access = conn.execute('''
            SELECT COUNT(*) as count FROM template_access 
            WHERE user_id = ? AND template_id = ? AND template_type = ? AND is_active = 1
        ''', (user_id, template_id, template_type)).fetchone()

        template_access_count = access['count'] if access else 0
        print(f"DEBUG: Individual template access count: {template_access_count}")

        # If no direct template access found, check if there are successful payments for this template
        if template_access_count == 0:
            successful_payments = conn.execute('''
                SELECT * FROM payments 
                WHERE user_id = ? AND status = 'settlement' 
                AND (order_id LIKE ? OR payment_type LIKE ?)
                ORDER BY created_at DESC
            ''', (user_id, f'TEMPLATE-{template_id}-%', f'template_{template_id}')).fetchall()

            print(f"DEBUG: Found {len(successful_payments)} successful payments for template {template_id}")

            # If there are successful payments, grant access automatically
            for payment in successful_payments:
                print(f"DEBUG: Auto-granting access based on successful payment: {payment['order_id']}")
                grant_success = grant_template_access(user_id, template_id, payment['id'])
                if grant_success:
                    template_access_count = 1
                    break

        # Also check all template access records for debugging
        all_access = conn.execute('''
            SELECT * FROM template_access WHERE user_id = ? AND template_type = ?
        ''', (user_id, template_type)).fetchall()

        print(f"DEBUG: All template access records for user {user_id}: {[dict(row) for row in all_access]}")

        conn.close()
        return template_access_count > 0

    except Exception as e:
        print(f"ERROR checking template access: {e}")
        if 'conn' in locals():
            try:
                conn.close()
            except:
                pass
        return False


@app.route('/api/template-status/<int:template_id>')
@require_auth
def template_status_api(template_id):
    """Secure API endpoint to get template status without exposing sensitive data"""
    try:
        user_id = session['user_id']

        # Use the enhanced validation function
        has_access, message = validate_template_access(user_id, template_id, 'wedding')

        # Get template basic info
        conn = get_db()
        template = conn.execute('SELECT id, name, is_premium, price FROM wedding_templates WHERE id = ?', 
                               (template_id,)).fetchone()
        conn.close()

        if not template:
            return jsonify({'error': 'Template not found'}), 404

        # Return minimal, secure data
        return jsonify({
            'template_id': template_id,
            'has_access': has_access,
            'is_premium': bool(template['is_premium']),
            'status_message': message,
            'template_name': template['name']
        })

    except Exception as e:
        print(f"Error in template status API: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Keep the old endpoint for backward compatibility but with limited data
@app.route('/check-template-access/<int:template_id>')
@require_auth  
def check_template_access_api(template_id):
    """Legacy API endpoint - redirects to new secure endpoint"""
    return template_status_api(template_id)

@app.route('/debug-template-access')
@require_auth
def debug_template_access():
    """Debug page to show all template access for current user"""
    user_id = session['user_id']

    try:
        conn = get_db()

        # Get all template access
        access_records = conn.execute('''
            SELECT ta.*, wt.name as template_name, p.order_id, p.status as payment_status
            FROM template_access ta
            LEFT JOIN wedding_templates wt ON ta.template_id = wt.id
            LEFT JOIN payments p ON ta.payment_id = p.id
            WHERE ta.user_id = ?
            ORDER BY ta.granted_at DESC
        ''', (user_id,)).fetchall()

        # Get user premium status
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

        # Get recent payments
        payments = conn.execute('''
            SELECT * FROM payments WHERE user_id = ? 
            ORDER BY created_at DESC LIMIT 10
        ''', (user_id,)).fetchall()

        conn.close()

        debug_data = {
            'user_id': user_id,
            'user': dict(user) if user else None,
            'access_records': [dict(row) for row in access_records],
            'recent_payments': [dict(row) for row in payments]
        }

        return f"<pre>{json.dumps(debug_data, indent=2, default=str)}</pre>"

    except Exception as e:
        return f"<pre>Error: {str(e)}</pre>"


@app.route("/preview-thumbnail/<int:template_id>")
def preview_thumbnail(template_id):
    # ambil data template dari DB
    template = query_db("SELECT * FROM wedding_templates WHERE id = ?",
                        [template_id],
                        one=True)
    if not template:
        return "Template not found", 404

    # contoh data dummy (biar semua field yang biasa dipakai template ada)
    sample_invitation = {
        'id': template['id'],
        'couple_name': 'Nimah & Fajar',
        'bride_name': 'Nimah',
        'bride_title': 'Prof',
        'bride_father': 'Bpk. Robert',
        'bride_mother': 'Ibu Edah',
        'groom_name': 'Fajar Julyana',
        'groom_title': 'Prof.',
        'groom_father': 'Bpk. Yayan',
        'groom_mother': 'Ibu Wawa',
        'wedding_date': datetime.strptime('2027-07-30', '%Y-%m-%d'),
        'wedding_time': '14:00',
        'venue_name': 'Trizara Resorts Glamping Lembang',
        'venue_address':
        'Jl. Pasir Wangi, Gudangkahuripan, Kec. Lembang, Kabupaten Bandung Barat, Jawa Barat 40391',

        # Multi-venue fields
        'akad_date': datetime.strptime('2027-07-30', '%Y-%m-%d'),
        'akad_time': '14:00',
        'akad_venue_name': 'Masjid Al-Ikhlas',
        'akad_venue_address':
        'Jl. Raya Lembang No. 123, Lembang, Bandung Barat',
        'resepsi_date': datetime.strptime('2027-07-30', '%Y-%m-%d'),
        'resepsi_time': '19:00',
        'resepsi_venue_name': 'Trizara Resorts Glamping Lembang',
        'resepsi_venue_address':
        'Jl. Pasir Wangi, Gudangkahuripan, Kec. Lembang, Kabupaten Bandung Barat, Jawa Barat 40391',

        # Optional family events
        'bride_event_date': datetime.strptime('2027-07-29', '%Y-%m-%d'),
        'bride_event_time': '16:00',
        'bride_event_venue_name': 'Kediaman Keluarga Mempelai Wanita',
        'bride_event_venue_address': 'https://maps.app.goo.gl/njsw3RbBFBAuZcB38',
        'groom_event_date': datetime.strptime('2027-07-31', '%Y-%m-%d'),
        'groom_event_time': '18:00',
        'groom_event_venue_name': 'Kediaman Keluarga Mempelai Pria',
        'groom_event_venue_address': 'https://maps.app.goo.gl/jBWJ9xTrSBTDNKxq6',
        'custom_message': 'Dengan penuh kebahagiaan, kami mengundang Anda',
        'color_scheme': template['color_scheme'],
        'template_name': template['name'],

        # field tambahan biar template lain tidak error
        'bank_name': 'MANDIRI',
        'bank_account': '1320026475575',
        'account_holder': 'Fajar Julyana',
        'qris_code': '',
        'guest_limit': 200,
        'is_active': 1,
        'invitation_link': 'preview-sample',
        'qr_code': '',
        'background_music': '',
        'ornaments': '',
    }

    print(f"DEBUG THUMBNAIL: Template ID {template_id}, file: {template['template_file']}")

    # Cari template di Documents/FajarMandiriStore/wedding_templates
    import os
    import glob

    template_file_raw = template['template_file']
    found_template_path = None

    template_path_docs = os.path.join(app.config['WEDDING_FOLDER'], template_file_raw)

    print(f"DEBUG THUMBNAIL: Checking Documents path: {template_path_docs}")

    if os.path.exists(template_path_docs):
        found_template_path = template_path_docs
        print(f"DEBUG THUMBNAIL: Found template in Documents: {template_path_docs}")
    else:
        # Coba cari dengan menghilangkan timestamp prefix
        if '_' in template_file_raw:
            parts = template_file_raw.split('_')
            if len(parts) > 1 and parts[0].isdigit():
                clean_name = '_'.join(parts[1:])
                clean_path = os.path.join(app.config['WEDDING_FOLDER'], clean_name)
                print(f"DEBUG THUMBNAIL: Trying clean name: {clean_path}")
                if os.path.exists(clean_path):
                    found_template_path = clean_path
                    print(f"DEBUG THUMBNAIL: Found clean template: {clean_path}")

        # Pattern matching sebagai fallback
        if not found_template_path:
            pattern = os.path.join(app.config['WEDDING_FOLDER'], f"*{template_file_raw}")
            matches = glob.glob(pattern)
            if matches:
                found_template_path = matches[0]
                print(f"DEBUG THUMBNAIL: Found via pattern: {found_template_path}")

    if not found_template_path:
        print(f"ERROR THUMBNAIL: Template not found in Documents: {template_file_raw}")
        return "Template not found in Documents folder", 404

    try:
        # Load template dari Documents folder
        print(f"DEBUG THUMBNAIL: Loading template from Documents: {found_template_path}")
        with open(found_template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()

        return render_template_string(template_content,
                                      invitation=sample_invitation,
                                      guests=[],
                                      prewedding_photos=prewedding_photos)
    except Exception as e:
        print(f"ERROR THUMBNAIL: Failed to load template: {str(e)}")
        return f"Error loading template: {str(e)}", 500


# Socket.IO Event Handlers
@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')


@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')


@socketio.on('join_room')
def handle_join_room(data):
    room = data['room']
    join_room(room)
    print(f'Client {request.sid} joined room {room}')


@socketio.on('leave_room')
def handle_leave_room(data):
    room = data['room']
    leave_room(room)
    print(f'Client {request.sid} left room {room}')


@socketio.on('send_message')
def handle_send_message(data):
    try:
        message = data['message']
        room = data['room']
        sender_type = data['sender_type']  # 'user', 'admin', 'guest'
        sender_name = data['sender_name']
        sender_email = data.get('sender_email', '')
        sender_id = data.get('sender_id')
        room_type = data.get('room_type', 'general')
        room_id = data.get('room_id', 'general')

        # Simpan ke database
        conn = get_db()
        conn.execute(
            '''
            INSERT INTO chat_messages
            (sender_type, sender_id, sender_name, sender_email, message, room_type, room_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (sender_type, sender_id, sender_name, sender_email, message,
              room_type, room_id))
        conn.commit()
        conn.close()

        # Broadcast ke semua user di room
        emit('receive_message', {
            'message': message,
            'sender_name': sender_name,
            'sender_type': sender_type,
            'timestamp': datetime.now().strftime('%H:%M'),
            'date': datetime.now().strftime('%Y-%m-%d')
        },
             room=room)

        print(f'Message sent to room {room}: {message}')

    except Exception as e:
        print(f'Error handling message: {str(e)}')
        emit('error', {'message': 'Failed to send message'})


# Chat Routes
@app.route('/chat')
def chat_page():
    """Chat page untuk user yang login"""
    if 'user_id' not in session and 'admin' not in session:
        flash('Silakan login untuk mengakses chat', 'warning')
        return redirect(url_for('login'))

    return render_template('chat.html')


@app.route('/api/chat/history/<room_type>/<room_id>')
def get_chat_history(room_type, room_id):
    """Get chat history untuk room tertentu"""
    conn = get_db()
    messages = conn.execute(
        '''
        SELECT * FROM chat_messages
        WHERE room_type = ? AND room_id = ?
        ORDER BY timestamp ASC
        LIMIT 50
    ''', (room_type, room_id)).fetchall()
    conn.close()

    message_list = []
    for msg in messages:
        message_list.append({
            'id': msg['id'],
            'sender_name': msg['sender_name'],
            'sender_type': msg['sender_type'],
            'message': msg['message'],
            'timestamp': msg['timestamp']
        })

    return jsonify(message_list)


@app.route('/admin/chat')
@require_admin
def admin_chat():
    """Admin chat dashboard"""
    conn = get_db()

    # Get recent messages grouped by room
    recent_messages = conn.execute('''
        SELECT DISTINCT room_type, room_id, sender_name, message, timestamp
        FROM chat_messages
        ORDER BY timestamp DESC
        LIMIT 20
    ''').fetchall()

    # Get unread message count
    unread_count = conn.execute('''
        SELECT COUNT(*) FROM chat_messages WHERE is_read = 0
    ''').fetchone()[0]

    conn.close()

    return render_template('admin/chat.html',
                           recent_messages=recent_messages,
                           unread_count=unread_count)


@app.route('/admin/chat/clear', methods=['POST'])
@require_admin
def clear_chat_history():
    """Clear chat history"""
    try:
        conn = get_db()
        conn.execute('DELETE FROM chat_messages')
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'Chat history cleared'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# ============================================================
# Fajar Mandiri Service Manager - Tray + Servers + Cloudflare
# File ini adalah bagian dari app.py (server web 5001)
# ============================================================

import os
import sys
import time
import threading
import subprocess
import webbrowser
import traceback
import platform
import socket as _socket
from pathlib import Path

import psutil
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw

# -------------------------------
# Konfigurasi path & konstanta
# -------------------------------
BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
CONFIG_DIR = BASE_DIR / "config"

CONFIG_FILE = CONFIG_DIR / "config.yml"
CERT_FILE = CONFIG_DIR / "cert.pem"
CREDENTIALS_FILE = next((p for p in CONFIG_DIR.glob("*.json")), None)  # optional

ICON_FILE = BASE_DIR / "icon.png"

# Deteksi binary cloudflared
import shutil
if platform.system() == "Windows":
    CF_BIN = BASE_DIR / "cloudflared.exe"
else:
    CF_BIN_PATH = shutil.which("cloudflared")
    if CF_BIN_PATH:
        CF_BIN = Path(CF_BIN_PATH)
    else:
        CF_BIN = BASE_DIR / "cloudflared"


# Perintah untuk menjalankan server Kasir jika tidak ada modul Python 'kasir_app'
# Ubah sesuai kebutuhan Anda (mis. jalankan uvicorn/flask/fastapi, dll)
KASIR_CMD_DEFAULT = [sys.executable, "kasir_app.py"]  # fallback

# -------------------------------
# State global
# -------------------------------
_threads = {
    "main": None,   # thread utk server web 5001 (socketio/app.run)
}
_procs = {
    "kasir": None,  # subprocess utk server kasir (5000) bila dijalankan sebagai proses terpisah
    "cloudflare": None,  # subprocess utk cloudflared
}

# -------------------------------
# Logging util
# -------------------------------
def _ts():
    return time.strftime("%Y-%m-%d %H:%M:%S")

def log_info(msg):
    print(f"[{_ts()}] INFO: {msg}")

def log_error(e, ctx=""):
    err = f"[{_ts()}] ERROR {ctx}: {e}\n{traceback.format_exc()}\n"
    print(err, file=sys.stderr)
    with open(BASE_DIR / "error_log.txt", "a", encoding="utf-8") as f:
        f.write(err)

# -------------------------------
# Network/Process utils
# -------------------------------
def is_port_in_use(port: int) -> bool:
    try:
        with _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            return s.connect_ex(("127.0.0.1", port)) == 0
    except Exception:
        return False

def kill_process_on_port(port: int) -> bool:
    """Bunuh proses yang sedang pakai port tertentu."""
    try:
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                for conn in proc.connections(kind="inet"):
                    if conn.laddr and conn.laddr.port == port:
                        log_info(f"Kill {proc.info['name']} (PID {proc.pid}) on port {port}")
                        proc.kill()
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        log_error(e, f"killing port {port}")
    return False

def _win_creationflags():
    if platform.system() == "Windows":
        # Hide console windows on Windows
        return subprocess.CREATE_NO_WINDOW
    return 0

# -------------------------------
# Browser opener (untuk domain publik)
# -------------------------------
def _open_browser_kiosk(url: str):
    try:
        if platform.system() == "Windows":
            try:
                subprocess.Popen(["cmd", "/c", f"start chrome --kiosk {url}"], shell=True)
            except Exception:
                webbrowser.open(url)
        else:
            webbrowser.open(url)
    except Exception as e:
        log_error(e, "opening browser")

# -------------------------------
# Server MAIN (5001) - current app.py
# -------------------------------
def _run_main_server():
    """
    Menjalankan server web (5001) dari objek `socketio` + `app` di file ini.
    - Memanggil init_db() jika tersedia.
    - Coba SocketIO dahulu; kalau gagal fallback ke app.run().
    """
    try:
        # Ambil objek dari global namespace file ini
        g = globals()
        init_db = g.get("init_db")
        app = g.get("app")
        socketio = g.get("socketio")

        if app is None:
            raise RuntimeError("Objek Flask `app` tidak ditemukan di app.py")
        if init_db:
            init_db()

        # Buka browser otomatis (domain publik)
        def _open():
            time.sleep(2)
            _open_browser_kiosk("https://fajarmandiri.store")
        threading.Thread(target=_open, daemon=True).start()

        # Jalankan
        try:
            if socketio:
                log_info("Starting MAIN server via SocketIO on port 5001")
                socketio.run(app,
                             host="0.0.0.0",
                             port=5001,
                             debug=False,
                             use_reloader=False,
                             allow_unsafe_werkzeug=True)
            else:
                raise RuntimeError("socketio tidak tersedia, fallback ke Flask app.run")
        except Exception as e:
            log_info(f"SocketIO failed: {e}. Fallback to app.run()")
            app.run(host="0.0.0.0", port=5001, debug=False, use_reloader=False)

    except Exception as e:
        log_error(e, "run_main_server")

def start_main(icon=None, item=None):
    """Start MAIN server (5001) di thread (karena ini app.py)."""
    th = _threads.get("main")
    if th and th.is_alive():
        log_info("MAIN server already running")
        return
    # Pastikan port bebas; kalau dipakai, kill
    if is_port_in_use(5001):
        log_info("Port 5001 in use, attempting to free it...")
        kill_process_on_port(5001)
        time.sleep(1)
    th = threading.Thread(target=_run_main_server, daemon=True)
    _threads["main"] = th
    th.start()
    log_info("MAIN server starting (5001)")

def stop_main(icon=None, item=None):
    """Matikan MAIN server dengan membunuh proses di port 5001 (karena berjalan via thread)."""
    if kill_process_on_port(5001):
        log_info("MAIN server stopped")
    else:
        log_info("MAIN server not running")

# -------------------------------
# Server KASIR (5000)
# -------------------------------
def _start_kasir_subprocess():
    """Jalankan kasir_app.py sebagai proses terpisah + buka browser http://localhost:5000"""
    if _procs["kasir"] and _procs["kasir"].poll() is None:
        log_info("KASIR server already running")
        return

    # Pastikan port 5000 bebas
    if is_port_in_use(5000):
        log_info("Port 5000 in use, attempting to free it...")
        kill_process_on_port(5000)
        time.sleep(1)

    try:
        cmd = [sys.executable, "kasir_app.py"]
        _procs["kasir"] = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=_win_creationflags()
        )
        log_info("KASIR server launching on http://localhost:5000")

        # Buka browser otomatis
        def open_browser():
            time.sleep(2)
            webbrowser.open("http://localhost:5000")
        threading.Thread(target=open_browser, daemon=True).start()

    except Exception as e:
        log_error(e, "start_kasir_subprocess")

def start_kasir(icon=None, item=None):
    _start_kasir_subprocess()

def stop_kasir(icon=None, item=None):
    if _procs["kasir"] and _procs["kasir"].poll() is None:
        log_info("Stopping KASIR server...")
        _procs["kasir"].terminate()
        try:
            _procs["kasir"].wait(timeout=5)
        except subprocess.TimeoutExpired:
            _procs["kasir"].kill()
        _procs["kasir"] = None
        log_info("KASIR server stopped")
    else:
        if kill_process_on_port(5000):
            log_info("KASIR server (by port kill) stopped")
        else:
            log_info("KASIR server not running")

# -------------------------------
# Cloudflare Tunnel
# -------------------------------
def start_tunnel(icon=None, item=None):
    if _procs["cloudflare"] and _procs["cloudflare"].poll() is None:
        log_info("Cloudflare tunnel already running")
        return
    if not CF_BIN.exists():
        log_info("cloudflared binary not found in app folder. Install manual terlebih dahulu.")
        return
    if not CONFIG_FILE.exists():
        log_info("config.yml tidak ditemukan di folder config/")
        return
    if not CERT_FILE.exists():
        log_info("cert.pem tidak ditemukan di folder config/")
        return

    cmd = [
        str(CF_BIN),
        "tunnel",
        "--config", str(CONFIG_FILE),
        "--origincert", str(CERT_FILE),
        "run"
    ]
    log_info(f"Starting Cloudflare tunnel: {' '.join(cmd)}")
    _procs["cloudflare"] = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=_win_creationflags())
    log_info("Cloudflare tunnel started")

def stop_tunnel(icon=None, item=None):
    if _procs["cloudflare"] and _procs["cloudflare"].poll() is None:
        log_info("Stopping Cloudflare tunnel...")
        _procs["cloudflare"].terminate()
        try:
            _procs["cloudflare"].wait(timeout=8)
        except subprocess.TimeoutExpired:
            _procs["cloudflare"].kill()
        _procs["cloudflare"] = None
        log_info("Cloudflare tunnel stopped")
    else:
        log_info("Cloudflare tunnel not running")

# -------------------------------
# Status helpers
# -------------------------------
def server_status_text():
    kasir = "Running" if (_procs["kasir"] and _procs["kasir"].poll() is None) or is_port_in_use(5000) else "Stopped"
    main_ = "Running" if is_port_in_use(5001) else "Stopped"
    tunnel = "Running" if (_procs["cloudflare"] and _procs["cloudflare"].poll() is None) else "Stopped"
    return f"Kasir: {kasir} | Main: {main_} | Tunnel: {tunnel}"

def open_local_kasir(icon=None, item=None):
    webbrowser.open("http://localhost:5000")

def open_local_main(icon=None, item=None):
    webbrowser.open("http://localhost:5001")

def open_public_kasir(icon=None, item=None):
    webbrowser.open("https://kasir.fajarmandiri.store")

def open_public_main(icon=None, item=None):
    webbrowser.open("https://fajarmandiri.store")

def open_config_folder(icon=None, item=None):
    path = str(CONFIG_DIR)
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception as e:
        log_error(e, "open_config_folder")

def open_logs_folder(icon=None, item=None):
    try:
        path = str(BASE_DIR)
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception as e:
        log_error(e, "open_logs_folder")

def show_system_info(icon=None, item=None):
    try:
        info = f"""
System: {platform.system()} {platform.release()} ({platform.machine()})
Python: {platform.python_version()}
Ports: 5000={'InUse' if is_port_in_use(5000) else 'Free'}, 5001={'InUse' if is_port_in_use(5001) else 'Free'}
Cloudflared: {'Found' if CF_BIN.exists() else 'Not Found'} ({CF_BIN})
Config: {CONFIG_FILE.exists()}, Cert: {CERT_FILE.exists()}, CredJSON: {bool(CREDENTIALS_FILE)}
Status: {server_status_text()}
""".strip()
        log_info(info)
    except Exception as e:
        log_error(e, "show_system_info")

# -------------------------------
# Mini Widget (GTK) - Optional for Linux desktop environments
# -------------------------------
try:
    from gi.repository import Gtk, GLib
    GTK_AVAILABLE = True
except ImportError:
    print("⚠️  GTK not available - GUI widgets disabled")
    GTK_AVAILABLE = False
    Gtk = None
    GLib = None

if GTK_AVAILABLE:
    class MiniWidget(Gtk.Window):
        def __init__(self):
            super().__init__(title="Fajar Mandiri Service")
            self.set_default_size(280, 200)
            self.set_keep_above(True)   # selalu di atas
            self.set_resizable(False)
            self.connect("destroy", self.on_quit)

            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            vbox.set_margin_top(10)
            vbox.set_margin_bottom(10)
            vbox.set_margin_start(10)
            vbox.set_margin_end(10)
            self.add(vbox)

            # Status
            self.status_label = Gtk.Label(label=f"Status: {server_status_text()}")
            vbox.pack_start(self.status_label, False, False, 0)

            # Tombol server kasir
            hbox_kasir = Gtk.Box(spacing=6)
            btn_start_kasir = Gtk.Button(label="Start Kasir")
            btn_start_kasir.connect("clicked", lambda _: start_kasir())
            hbox_kasir.pack_start(btn_start_kasir, True, True, 0)

            btn_stop_kasir = Gtk.Button(label="Stop Kasir")
            btn_stop_kasir.connect("clicked", lambda _: stop_kasir())
            hbox_kasir.pack_start(btn_stop_kasir, True, True, 0)
            vbox.pack_start(hbox_kasir, False, False, 0)

            # Tombol server utama
            hbox_main = Gtk.Box(spacing=6)
            btn_start_main = Gtk.Button(label="Start Main")
            btn_start_main.connect("clicked", lambda _: start_main())
            hbox_main.pack_start(btn_start_main, True, True, 0)

            btn_stop_main = Gtk.Button(label="Stop Main")
            btn_stop_main.connect("clicked", lambda _: stop_main())
            hbox_main.pack_start(btn_stop_main, True, True, 0)
            vbox.pack_start(hbox_main, False, False, 0)

            # Tombol tunnel
            hbox_tunnel = Gtk.Box(spacing=6)
            btn_start_tunnel = Gtk.Button(label="Start Tunnel")
            btn_start_tunnel.connect("clicked", lambda _: start_tunnel())
            hbox_tunnel.pack_start(btn_start_tunnel, True, True, 0)

            btn_stop_tunnel = Gtk.Button(label="Stop Tunnel")
            btn_stop_tunnel.connect("clicked", lambda _: stop_tunnel())
            hbox_tunnel.pack_start(btn_stop_tunnel, True, True, 0)
            vbox.pack_start(hbox_tunnel, False, False, 0)

            # Tombol Quit
            btn_quit = Gtk.Button(label="Quit")
            btn_quit.connect("clicked", self.on_quit)
            vbox.pack_start(btn_quit, False, False, 0)

            # Update status tiap 5 detik
            GLib.timeout_add_seconds(5, self.refresh_status)

        def refresh_status(self):
            try:
                self.status_label.set_text(f"Status: {server_status_text()}")
            except Exception as e:
                log_error(e, "refresh_status")
            return True

        def on_quit(self, *args):
            try:
                stop_tunnel()
                stop_kasir()
                stop_main()
            except Exception as e:
                log_error(e, "quit_application cleanup")
            log_info("Application shutdown complete")
            Gtk.main_quit()
            os._exit(0)
else:
    # Dummy MiniWidget class when GTK is not available
    class MiniWidget:
        def __init__(self):
            print("⚠️  MiniWidget GTK interface not available")

        def refresh_status(self):
            pass

        def on_quit(self, *args):
            pass


def run_widget():
    if GTK_AVAILABLE:
        win = MiniWidget()
        win.show_all()
        Gtk.main()
    else:
        print("⚠️  GUI widget not available - running without GTK interface")

# -------------------------------
# MAIN ENTRYPOINT
# -------------------------------
if __name__ == "__main__":
    # Auto-start MAIN (port 5001) karena ini app.py web server
    start_main()
    # Tunggu beberapa detik agar web sudah siap
    time.sleep(5)
    # (opsional) Auto-start KASIR & Tunnel:
    # start_kasir()
    start_tunnel()
    run_widget()

    # Jaga proses utama tetap hidup
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        quit_application()