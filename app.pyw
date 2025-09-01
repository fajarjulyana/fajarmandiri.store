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
from jinja2 import TemplateNotFound, Template


app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
# Path universal ke Documents user
USER_DOCS = os.path.join(os.path.expanduser("~"), "Documents", "FajarMandiriStore")

# Penting: hanya ada baris ini untuk socketio
# Fix untuk PyInstaller - coba berbagai async_mode secara bertahap
def create_socketio():
    """Create SocketIO instance with fallback modes for PyInstaller compatibility"""
    modes_to_try = ['threading', 'eventlet', None]

    for mode in modes_to_try:
        try:
            if mode is None:
                print(f"Trying SocketIO without async_mode (auto-detect)")
                return SocketIO(app, cors_allowed_origins="*", logger=False, engineio_logger=False)
            else:
                print(f"Trying SocketIO with async_mode: {mode}")
                return SocketIO(app, cors_allowed_origins="*", async_mode=mode, logger=False, engineio_logger=False)
        except Exception as e:
            print(f"Failed to create SocketIO with async_mode={mode}: {str(e)}")
            continue

    # Ultimate fallback - basic SocketIO without any special config
    print("Using basic SocketIO configuration as final fallback")
    return SocketIO(app, cors_allowed_origins="*", logger=False, engineio_logger=False)

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
app.config['TEMPLATES_FOLDER'] = 'cv_templates'
app.config['WEDDING_FOLDER'] = 'wedding_templates'
app.config['MUSIC_FOLDER'] = os.path.join(USER_DOCS, "music")
app.config['PREWEDDING_FOLDER'] = os.path.join(USER_DOCS, "prewedding_photos")

# Create necessary directories
for folder in [app.config['UPLOAD_FOLDER'], app.config['TEMPLATES_FOLDER'],
               app.config['WEDDING_FOLDER'], app.config['MUSIC_FOLDER'],
               app.config['PREWEDDING_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

# Authentication decorators
from functools import wraps

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' not in session:
            flash('Akses ditolak! Silakan login sebagai admin', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def require_guest_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' in session:
            return redirect(url_for('dashboard'))
        elif 'admin' in session:
            return redirect(url_for('admin_dashboard'))
        return f(*args, **kwargs)
    return decorated_function


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
        templates = conn.execute('SELECT id, name, template_file FROM wedding_templates').fetchall()

        # Available template files
        template_files = [
            'MandiriTheme_Style.html',
            'MandiriTheme_Style_1.html',
            'MandiriTheme_Style_2.html',
            'MandiriTheme_Style_3.html',
            'MandiriTheme_classic.html',
            'MandiriTheme_elegant.html',
            'MandiriTheme_modern.html',
            'classic_romance.html',
            'elegant_cream.html',
            'elegant_golden.html',
            'garden_fresh.html',
            'garden_romance.html',
            'luxury_modern.html',
            'minimal_blush.html',
            'modern_minimalist.html',
            'ocean_waves.html',
            'royal_burgundy.html',
            'vintage_charm.html'
        ]

        updated_count = 0
        for i, template in enumerate(templates):
            if not template['template_file'] or template['template_file'] == '':
                # Assign template file based on index or name
                if i < len(template_files):
                    new_template_file = template_files[i]
                else:
                    # Use MandiriTheme_Style.html as default
                    new_template_file = 'MandiriTheme_Style.html'

                print(f"Updating template {template['name']} (ID: {template['id']}) with file: {new_template_file}")
                conn.execute(
                    'UPDATE wedding_templates SET template_file = ? WHERE id = ?',
                    (new_template_file, template['id'])
                )
                updated_count += 1

        if updated_count > 0:
            conn.commit()
            print(f"Updated {updated_count} templates with missing template files")
        else:
            print("All templates have template files assigned")

        conn.close()

    except Exception as e:
        print(f"Error checking template files: {str(e)}")

def reset_database():
    """Reset database dan buat ulang dengan struktur yang benar"""
    try:
        # Backup existing database
        if os.path.exists('fajarmandiri.db'):
            import shutil
            shutil.copy('fajarmandiri.db', f'wedding_app_backup_{int(datetime.now().timestamp())}.db')

        # Hapus database lama
        if os.path.exists('fajarmandiri.db'):
            os.remove('fajarmandiri.db')

        print("Database lama dihapus, membuat database baru...")
        init_db()
        print("Database baru berhasil dibuat!")

    except Exception as e:
        print(f"Error reset database: {str(e)}")

DB_FILE = "fajarmandiri.db"

def init_db():
    # Jika file DB sudah ada, cek apakah tabel chat_messages ada
    if os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Cek apakah tabel chat_messages ada
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='chat_messages'
        """)
        chat_table_exists = cursor.fetchone()

        if not chat_table_exists:
            # Tambah tabel chat_messages jika belum ada
            print("Menambahkan tabel chat_messages yang hilang...")
            cursor.execute('''CREATE TABLE chat_messages (
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
            conn.commit()
            print("Tabel chat_messages berhasil ditambahkan!")

        conn.close()
        print("Database sudah ada, validasi selesai.")
        return

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    print("Membuat struktur database...")

    # Users table
    c.execute('''CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        google_id TEXT,
        email TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        password TEXT,
        picture TEXT,
        is_premium BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Orders table
    c.execute('''CREATE TABLE orders (
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
    c.execute('''CREATE TABLE cv_templates (
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
    c.execute('''CREATE TABLE wedding_templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        category TEXT,
        template_file TEXT NOT NULL,
        preview_image TEXT,
        color_scheme TEXT,
        animations TEXT,
        background_music TEXT,
        ornaments TEXT,
        is_premium BOOLEAN DEFAULT 0,
        price INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Wedding invitations table
    c.execute('''CREATE TABLE wedding_invitations (
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
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (template_id) REFERENCES wedding_templates (id)
    )''')

    # Wedding guests table
    c.execute('''CREATE TABLE wedding_guests (
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

    # Admin table
    c.execute('''CREATE TABLE admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    )''')

    # Chat messages table
    c.execute('''CREATE TABLE chat_messages (
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

    # Insert default admin
    hashed_password = generate_password_hash('fajar123')
    c.execute('INSERT INTO admin (username, password) VALUES (?, ?)',
              ('fajar', hashed_password))
    print("Admin default dibuat: username=fajar, password=fajar123")

    conn.commit()
    conn.close()


def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn



from flask import send_from_directory, abort
import os

@app.route('/documents/<path:filename>')
def serve_documents(filename):
    """Serve files from Documents folder"""
    try:
        return send_from_directory(USER_DOCS, filename)
    except Exception as e:
        print(f"Error serving document {filename}: {str(e)}")
        abort(404)

@app.route('/uploaded/<path:filename>')
def uploaded_file(filename):
    """Alias for uploaded files - matches template expectations"""
    try:
        return send_from_directory(USER_DOCS, filename)
    except Exception as e:
        print(f"Error serving uploaded file {filename}: {str(e)}")
        abort(404)

@app.route('/documents/js/<path:filename>')
def serve_documents_js(filename):
    """Serve JS files from Documents folder"""
    try:
        js_path = os.path.join(USER_DOCS, 'js')
        return send_from_directory(js_path, filename)
    except Exception as e:
        print(f"Error serving JS document {filename}: {str(e)}")
        abort(404)

@app.route('/documents/music/<path:filename>')
def serve_documents_music(filename):
    """Serve music files from Documents folder"""
    try:
        music_path = os.path.join(USER_DOCS, 'music')
        return send_from_directory(music_path, filename)
    except Exception as e:
        print(f"Error serving music document {filename}: {str(e)}")
        abort(404)


# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
@require_guest_only
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
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
        existing_user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

        if existing_user:
            flash('Email sudah terdaftar!', 'error')
            conn.close()
            return render_template('auth/register.html')

        hashed_password = generate_password_hash(password)
        cursor = conn.execute('''
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
            oauth_config,
            scopes=['openid', 'email', 'profile']
        )
        flow.redirect_uri = url_for('oauth2callback', _external=True)
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        session['state'] = state
        return redirect(authorization_url)
    else:
        flash('Google OAuth tidak dikonfigurasi. Silakan daftar manual.', 'error')
        return redirect(url_for('register'))

@app.route('/oauth2callback')
def oauth2callback():
    state = session['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        oauth_config,
        scopes=['openid', 'email', 'profile'],
        state=state
    )
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    request_session = google.auth.transport.requests.Request()

    service = build('oauth2', 'v2', credentials=credentials)
    user_info = service.userinfo().get().execute()

    conn = get_db()
    existing_user = conn.execute('SELECT * FROM users WHERE google_id = ?', (user_info['id'],)).fetchone()

    if existing_user:
        user_id = existing_user['id']
        is_premium = existing_user['is_premium']
    else:
        cursor = conn.execute(
            'INSERT INTO users (google_id, email, name, picture, is_premium) VALUES (?, ?, ?, ?, ?)',
            (user_info['id'], user_info['email'], user_info['name'], user_info.get('picture', ''), 0)
        )
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
        # Get stats for homepage
        conn = get_db()
        stats = {
            'total_invitations': conn.execute('SELECT COUNT(*) FROM wedding_invitations').fetchone()[0],
            'total_users': conn.execute('SELECT COUNT(*) FROM users').fetchone()[0],
            'premium_templates': conn.execute('SELECT COUNT(*) FROM wedding_templates WHERE is_premium = 1').fetchone()[0],
            'total_guests': conn.execute('SELECT COUNT(*) FROM wedding_guests').fetchone()[0]
        }

        # Get sample templates for showcase
        wedding_templates = conn.execute('SELECT * FROM wedding_templates ORDER BY is_premium, name LIMIT 6').fetchall()
        cv_templates = conn.execute('SELECT * FROM cv_templates ORDER BY is_premium, name LIMIT 6').fetchall()

        conn.close()
        return render_template('index.html', stats=stats, wedding_templates=wedding_templates, cv_templates=cv_templates)

@app.route('/dashboard')
@require_auth
def dashboard():
    conn = get_db()

    # Get user's recent wedding invitations
    invitations = conn.execute(
        'SELECT * FROM wedding_invitations WHERE user_id = ? ORDER BY created_at DESC LIMIT 3',
        (session['user_id'],)
    ).fetchall()

    print(f"Debug Dashboard - User ID: {session['user_id']}, Found {len(invitations)} invitations")

    # Get user's recent orders
    orders = conn.execute(
        'SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC LIMIT 5',
        (session['user_id'],)
    ).fetchall()

    conn.close()

    return render_template('dashboard.html', invitations=invitations, orders=orders)

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
                file_path = os.path.join(app.config['PREWEDDING_FOLDER'], filename)
                file.save(file_path)
                file_path = filename

        conn = get_db()
        conn.execute('''
            INSERT INTO orders (user_id, nama, email, whatsapp, jenis_cetakan, ukuran, jumlah, warna, kertas, catatan, file_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session.get('user_id'), nama, email, whatsapp, jenis_cetakan, ukuran, jumlah, warna, kertas, catatan, file_path))
        conn.commit()
        conn.close()

        flash('Pesanan berhasil dibuat! Kami akan segera menghubungi Anda.', 'success')

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
        (session['user_id'],)
    ).fetchall()
    conn.close()

    return render_template('my_orders.html', orders=orders)

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

    return render_template('status.html', orders=orders, search=search, status_filter=status_filter)

# CV Generator routes
@app.route('/cv-generator')
@require_auth
def cv_generator():
    conn = get_db()
    templates = conn.execute('SELECT * FROM cv_templates ORDER BY is_premium, name').fetchall()
    conn.close()

    return render_template('cv_generator.html', templates=templates)

@app.route('/generate-cv', methods=['POST'])
@require_auth
def generate_cv():
    template_id = request.form.get('template_id')

    conn = get_db()
    template = conn.execute('SELECT * FROM cv_templates WHERE id = ?', (template_id,)).fetchone()
    conn.close()

    if not template:
        flash('Template tidak ditemukan!', 'error')
        return redirect(url_for('cv_generator'))

    if template['is_premium'] and not session.get('is_premium'):
        flash('Template premium memerlukan akun premium!', 'error')
        return redirect(url_for('cv_generator'))

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
                    'institusi': request.form.getlist('pendidikan_institusi')[i],
                    'jurusan': request.form.getlist('pendidikan_jurusan')[i] if i < len(request.form.getlist('pendidikan_jurusan')) else '',
                    'tahun': request.form.getlist('pendidikan_tahun')[i] if i < len(request.form.getlist('pendidikan_tahun')) else ''
                })

    if request.form.getlist('pengalaman_perusahaan'):
        for i in range(len(request.form.getlist('pengalaman_perusahaan'))):
            if request.form.getlist('pengalaman_perusahaan')[i]:
                cv_data['pengalaman'].append({
                    'perusahaan': request.form.getlist('pengalaman_perusahaan')[i],
                    'posisi': request.form.getlist('pengalaman_posisi')[i] if i < len(request.form.getlist('pengalaman_posisi')) else '',
                    'periode': request.form.getlist('pengalaman_periode')[i] if i < len(request.form.getlist('pengalaman_periode')) else '',
                    'deskripsi': request.form.getlist('pengalaman_deskripsi')[i] if i < len(request.form.getlist('pengalaman_deskripsi')) else ''
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

    return render_template('cv_preview.html', cv_data=cv_data, template=template)

# Wedding Invitation routes
@app.route('/wedding-invitations')
@require_auth
def wedding_invitations():
    conn = get_db()
    invitations = conn.execute(
        'SELECT * FROM wedding_invitations WHERE user_id = ? ORDER BY created_at DESC',
        (session['user_id'],)
    ).fetchall()

    # Debug: Print info
    print(f"Debug - User ID: {session['user_id']}")
    print(f"Debug - Found {len(invitations)} invitations")
    for inv in invitations:
        print(f"Debug - Invitation: {inv['couple_name']} (ID: {inv['id']})")

    conn.close()

    return render_template('wedding_invitations.html', invitations=invitations)

@app.route('/create-wedding-invitation', methods=['GET', 'POST'])
@require_auth
def create_wedding_invitation():
    # Verifikasi user session
    if 'user_id' not in session:
        flash('Session expired, silakan login ulang!', 'error')
        return redirect(url_for('login'))

    print(f"Debug - Create Wedding - User ID: {session['user_id']}")
    print(f"Debug - Create Wedding - User Name: {session.get('user_name', 'Unknown')}")

    if request.method == 'POST':
        # Required fields
        bride_name = request.form['bride_name']
        bride_title = request.form.get('bride_title', '')
        bride_father = request.form['bride_father']
        bride_mother = request.form['bride_mother']
        groom_name = request.form['groom_name']
        groom_title = request.form.get('groom_title', '')
        groom_father = request.form['groom_father']
        groom_mother = request.form['groom_mother']

        couple_name = f"{bride_name} & {groom_name}"
        template_id = int(request.form.get('template_id', 1))
        custom_message = request.form.get('custom_message', '')
        guest_limit = int(request.form.get('guest_limit', 100))

        # Event type handling
        event_type = request.form.get('event_type', 'single')

        # Initialize venue variables
        wedding_date = ''
        wedding_time = ''
        venue_name = ''
        venue_address = ''
        akad_date = ''
        akad_time = ''
        akad_venue_name = ''
        akad_venue_address = ''
        resepsi_date = ''
        resepsi_time = ''
        resepsi_venue_name = ''
        resepsi_venue_address = ''
        bride_event_date = ''
        bride_event_time = ''
        bride_event_venue_name = ''
        bride_event_venue_address = ''
        groom_event_date = ''
        groom_event_time = ''
        groom_event_venue_name = ''
        groom_event_venue_address = ''

        if event_type == 'single':
            # Single event - use legacy fields
            wedding_date = request.form.get('wedding_date', '')
            wedding_time = request.form.get('wedding_time', '')
            venue_name = request.form.get('venue_name', '')
            venue_address = request.form.get('venue_address', '')

            # Also populate akad and resepsi with same data for template compatibility
            akad_date = wedding_date
            akad_time = wedding_time
            akad_venue_name = venue_name
            akad_venue_address = venue_address
            resepsi_date = wedding_date
            resepsi_time = wedding_time
            resepsi_venue_name = venue_name
            resepsi_venue_address = venue_address
        else:
            # Separate events
            akad_date = request.form.get('akad_date', '')
            akad_time = request.form.get('akad_time', '')
            akad_venue_name = request.form.get('akad_venue_name', '')
            akad_venue_address = request.form.get('akad_venue_address', '')

            resepsi_date = request.form.get('resepsi_date', '')
            resepsi_time = request.form.get('resepsi_time', '')
            resepsi_venue_name = request.form.get('resepsi_venue_name', '')
            resepsi_venue_address = request.form.get('resepsi_venue_address', '')

            # Optional family events
            bride_event_date = request.form.get('bride_event_date', '')
            bride_event_time = request.form.get('bride_event_time', '')
            bride_event_venue_name = request.form.get('bride_event_venue_name', '')
            bride_event_venue_address = request.form.get('bride_event_venue_address', '')

            groom_event_date = request.form.get('groom_event_date', '')
            groom_event_time = request.form.get('groom_event_time', '')
            groom_event_venue_name = request.form.get('groom_event_venue_name', '')
            groom_event_venue_address = request.form.get('groom_event_venue_address', '')

            # Set legacy fields to first available event for backwards compatibility
            if akad_date:
                wedding_date = akad_date
                wedding_time = akad_time
                venue_name = akad_venue_name
                venue_address = akad_venue_address
            elif resepsi_date:
                wedding_date = resepsi_date
                wedding_time = resepsi_time
                venue_name = resepsi_venue_name
                venue_address = resepsi_venue_address
        bank_name = request.form.get('bank_name', '')
        bank_account = request.form.get('bank_account', '')
        account_holder = request.form.get('account_holder', '')

        # Generate unique invitation link
        invitation_code = str(uuid.uuid4())[:8]
        invitation_link = f"{bride_name.lower().replace(' ', '')}-{groom_name.lower().replace(' ', '')}-{invitation_code}"

        # Handle background music
        background_music = ''
        music_option = request.form.get('music_option', 'none')

        if music_option == 'default':
            # Use default music - pastikan file default ada
            selected_music = request.form.get('default_background_music', '')
            if selected_music:
                background_music = selected_music
            else:
                background_music = 'default_wedding.mp3'  # fallback default
        elif music_option == 'custom' and 'background_music' in request.files:
            # Handle custom music upload
            music_file = request.files['background_music']
            if music_file.filename != '':
                filename = secure_filename(music_file.filename)
                timestamp = str(int(datetime.now().timestamp()))
                filename = f"{timestamp}_{filename}"
                music_path = os.path.join(app.config['MUSIC_FOLDER'], filename)
                music_file.save(music_path)
                background_music = filename

        # Handle prewedding photos (max 10)
        prewedding_photos = []
        for i in range(10):
            if f'prewedding_photo_{i}' in request.files:
                photo = request.files[f'prewedding_photo_{i}']
                if photo.filename != '':
                    filename = secure_filename(photo.filename)
                    timestamp = str(int(datetime.now().timestamp()))
                    filename = f"{timestamp}_{i}_{filename}"
                    # Simpan ke Documents/FajarMandiriStore/prewedding_photos agar bisa diakses web
                    photo_path = os.path.join(app.config['PREWEDDING_FOLDER'], filename)
                    os.makedirs(app.config['PREWEDDING_FOLDER'], exist_ok=True)
                    photo.save(photo_path)


                    # Ambil orientasi dari form (manual selection)
                    orientation_key = f'photo_orientation_{i}'
                    orientation = request.form.get(orientation_key, '').lower()

                    # Validasi orientasi, jika kosong gunakan auto-detect sebagai fallback
                    if orientation not in ['portrait', 'landscape']:
                        try:
                            with Image.open(photo_path) as img:
                                width, height = img.size
                                orientation = "portrait" if height > width else "landscape"
                                print(f"Auto-detected orientation for {filename}: {width}x{height} = {orientation}")
                        except Exception as e:
                            print(f"Error processing photo {filename}: {str(e)}")
                            orientation = "landscape"  # fallback default
                    else:
                        print(f"Manual orientation for {filename}: {orientation}")

                    prewedding_photos.append({
                        "filename": filename,
                        "orientation": orientation
                    })

        print(f"DEBUG: Total photos processed: {len(prewedding_photos)}")
        for photo in prewedding_photos:
            print(f"  - {photo['filename']} ({photo['orientation']})")

        # Handle QRIS upload
        qris_code = ''
        if 'qris_code' in request.files:
            qris_file = request.files['qris_code']
            if qris_file.filename != '':
                qris_data = qris_file.read()
                qris_code = base64.b64encode(qris_data).decode()

        # Generate QR Code for invitation
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url_for('view_wedding_invitation', link=invitation_link, _external=True))
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

        # Validasi input - hanya field essential yang wajib
        missing_fields = []
        if not bride_name.strip():
            missing_fields.append('Nama Mempelai Wanita')
        if not bride_father.strip():
            missing_fields.append('Nama Ayah Mempelai Wanita')
        if not bride_mother.strip():
            missing_fields.append('Nama Ibu Mempelai Wanita')
        if not groom_name.strip():
            missing_fields.append('Nama Mempelai Pria')
        if not groom_father.strip():
            missing_fields.append('Nama Ayah Mempelai Pria')
        if not groom_mother.strip():
            missing_fields.append('Nama Ibu Mempelai Pria')

        # Venue validation based on event type
        if event_type == 'single':
            if not venue_address.strip():
                missing_fields.append('Alamat Venue')
        # For separate events, validation is optional since some couples might only have one event

        if missing_fields:
            flash(f'Field berikut wajib diisi: {", ".join(missing_fields)}', 'error')
            conn = get_db()
            wedding_templates = conn.execute('SELECT * FROM wedding_templates ORDER BY id ASC').fetchall()
            conn.close()
            return render_template('create_wedding_invitation.html', wedding_templates=wedding_templates)

        # Debug: Print data sebelum insert
        print(f"Debug - Data undangan: {bride_name} & {groom_name}")
        print(f"Debug - User ID: {session.get('user_id')}")
        print(f"Debug - Link: {invitation_link}")
        print(f"Debug - Template ID: {template_id}")
        print(f"Debug - Couple Name: {couple_name}")
        print(f"Debug - Wedding Date: {wedding_date}")
        print(f"Debug - Wedding Time: {wedding_time}")
        print(f"Debug - Venue Name: {venue_name}")
        print(f"Debug - Venue Address: {venue_address}")
        print(f"Debug - Custom Message: {custom_message}")
        print(f"Debug - Guest Limit: {guest_limit}")

        # Debug form data yang diterima
        print("Debug - Form data received:")
        for key, value in request.form.items():
            print(f"  {key}: {value}")
        print("Debug - Files received:")
        for key, file in request.files.items():
            if file.filename:
                print(f"  {key}: {file.filename}")

        try:
            conn = get_db()

            # Test koneksi database dulu
            test_query = conn.execute('SELECT COUNT(*) FROM wedding_invitations').fetchone()
            print(f"Debug - Total undangan di database: {test_query[0]}")

            # Convert empty strings to None for dates
            wedding_date_final = wedding_date if wedding_date else None
            wedding_time_final = wedding_time if wedding_time else None

            # Insert undangan baru
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
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (session['user_id'], couple_name, bride_name, bride_title, bride_father, bride_mother,
                  groom_name, groom_title, groom_father, groom_mother, wedding_date_final, wedding_time_final, venue_name,
                  venue_address, template_id, custom_message, invitation_link, qr_code_base64, background_music,
                  json.dumps(prewedding_photos), bank_name, bank_account, account_holder, qris_code, guest_limit,
                  akad_date or None, akad_time or None, akad_venue_name or None, akad_venue_address or None,
                  resepsi_date or None, resepsi_time or None, resepsi_venue_name or None, resepsi_venue_address or None,
                  bride_event_date or None, bride_event_time or None, bride_event_venue_name or None, bride_event_venue_address or None,
                  groom_event_date or None, groom_event_time or None, groom_event_venue_name or None, groom_event_venue_address or None))

            invitation_id = cursor.lastrowid
            conn.commit()

            # Verifikasi data tersimpan
            verify = conn.execute('SELECT * FROM wedding_invitations WHERE id = ?', (invitation_id,)).fetchone()
            if verify:
                print(f"Debug - Undangan berhasil disimpan: {verify['couple_name']}")
            else:
                print("Debug - ERROR: Data tidak tersimpan!")

            conn.close()

            flash(f'Undangan pernikahan "{couple_name}" berhasil dibuat!', 'success')
            return redirect(url_for('wedding_invitations'))

        except sqlite3.Error as e:
            print(f"Database Error: {str(e)}")
            flash(f'Database Error: {str(e)}', 'error')
            if 'conn' in locals():
                conn.close()
            return redirect(url_for('create_wedding_invitation'))
        except Exception as e:
            print(f"General Error: {str(e)}")
            flash(f'Error: {str(e)}', 'error')
            if 'conn' in locals():
                conn.close()
            return redirect(url_for('create_wedding_invitation'))

    conn = get_db()
    wedding_templates = conn.execute('SELECT * FROM wedding_templates ORDER BY id ASC').fetchall()
    conn.close()

    return render_template('create_wedding_invitation.html', wedding_templates=wedding_templates)

@app.route('/wedding/preview-template/<int:template_id>')
def preview_wedding_template(template_id):
    try:
        conn = get_db()
        template = conn.execute('SELECT * FROM wedding_templates WHERE id = ?', (template_id,)).fetchone()
        conn.close()

        if not template:
            return "Template not found", 404

        # Sample data untuk preview (sesuai dengan yang ada di preview_thumbnail)
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
            'venue_address': 'Jl. Pasir Wangi, Gudangkahuripan, Kec. Lembang, Kabupaten Bandung Barat, Jawa Barat 40391',

            # Multi-venue fields
            'akad_date': datetime.strptime('2027-07-30', '%Y-%m-%d'),
            'akad_time': '14:00',
            'akad_venue_name': 'Masjid Al-Ikhlas',
            'akad_venue_address': 'Jl. Raya Lembang No. 123, Lembang, Bandung Barat',

            'resepsi_date': datetime.strptime('2027-07-30', '%Y-%m-%d'),
            'resepsi_time': '19:00',
            'resepsi_venue_name': 'Trizara Resorts Glamping Lembang',
            'resepsi_venue_address': 'Jl. Pasir Wangi, Gudangkahuripan, Kec. Lembang, Kabupaten Bandung Barat, Jawa Barat 40391',

            # Optional family events
            'bride_event_date': datetime.strptime('2027-07-29', '%Y-%m-%d'),
            'bride_event_time': '16:00',
            'bride_event_venue_name': 'Kediaman Keluarga Mempelai Wanita',
            'bride_event_venue_address': 'Jl. Keluarga No. 45, Bandung',

            'groom_event_date': datetime.strptime('2027-07-31', '%Y-%m-%d'),
            'groom_event_time': '18:00',
            'groom_event_venue_name': 'Kediaman Keluarga Mempelai Pria',
            'groom_event_venue_address': 'Jl. Keluarga Pria No. 67, Cimahi',

            'custom_message': 'Dengan penuh kebahagiaan, kami mengundang Anda',
            'color_scheme': template['color_scheme'],
            'template_name': template['name'],

            # Additional fields
            'bank_name': 'MANDIRI',
            'bank_account': '1320026475575',
            'account_holder': 'Fajar Julyana',
            'qris_code': '',
            'guest_limit': 200,
            'invitation_link': 'preview-sample',
            'qr_code': '',
            'background_music': 'default_wedding.mp3',
            'ornaments': '',
        }

        # Debug log untuk melihat path yang dicoba
        documents_path = os.path.join(USER_DOCS, 'wedding_templates', template['template_file'])
        app_folder_path = os.path.join('templates', 'wedding_templates', template['template_file'])

        print(f"DEBUG PREVIEW: Checking documents path: {documents_path}")
        print(f"DEBUG PREVIEW: Checking app path: {app_folder_path}")

        # Coba load dari Documents folder dulu dengan proper Jinja2 rendering
        if os.path.exists(documents_path):
            print(f"DEBUG PREVIEW: Loading from documents folder with Jinja2 rendering")
            with open(documents_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Render template string dengan Jinja2
            from jinja2 import Template
            jinja_template = Template(template_content)
            return jinja_template.render(
                invitation=sample_invitation,
                guests=[],
                prewedding_photos=[],
                url_for=url_for  # Pass url_for function untuk template
            )
        else:
            # Fallback ke app folder jika tidak ada di Documents
            print(f"DEBUG PREVIEW: Documents not found, trying app folder")
            try:
                return render_template(
                    f'wedding_templates/{template["template_file"]}',
                    invitation=sample_invitation,
                    guests=[],
                    prewedding_photos=[]
                )
            except TemplateNotFound:
                return "Template tidak ditemukan di Documents maupun app folder", 404

    except Exception as e:
        print(f"Error previewing template: {str(e)}")
        return f"Error: {str(e)}", 500


@app.route('/api/wedding-templates')
def api_wedding_templates():
    """API endpoint for wedding templates"""
    conn = get_db()
    templates = conn.execute('SELECT * FROM wedding_templates ORDER BY is_premium, name').fetchall()
    conn.close()

    templates_list = []
    for template in templates:
        templates_list.append({
            'id': template['id'],
            'name': template['name'],
            'description': template['description'],
            'category': template['category'],
            'preview_image': f"/static/images/wedding_templates/{template['preview_image']}" if template['preview_image'] else '/static/images/wedding_templates/default_preview.jpg',
            'is_premium': bool(template['is_premium']),
            'price': template['price'] or 0,
            'color_scheme': template['color_scheme'],
            'animations': template['animations']
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
        (link,)
    ).fetchone()

    if not invitation:
        return render_template('404.html'), 404

    guests = conn.execute(
        'SELECT * FROM wedding_guests WHERE invitation_id = ? ORDER BY created_at DESC',
        (invitation['id'],)
    ).fetchall()

    conn.close()

    # Convert invitation to dict for manipulation
    invitation_dict = dict(invitation)

    # Convert wedding_date string to datetime object if it exists
    if invitation_dict.get('wedding_date'):
        try:
            from datetime import datetime
            invitation_dict['wedding_date'] = datetime.strptime(invitation_dict['wedding_date'], '%Y-%m-%d')
        except (ValueError, TypeError):
            invitation_dict['wedding_date'] = None

    # Convert other date fields if they exist
    for date_field in ['akad_date', 'resepsi_date', 'bride_event_date', 'groom_event_date']:
        if invitation_dict.get(date_field):
            try:
                invitation_dict[date_field] = datetime.strptime(invitation_dict[date_field], '%Y-%m-%d')
            except (ValueError, TypeError):
                invitation_dict[date_field] = None

    # Parse prewedding photos with enhanced debugging
    prewedding_photos = []
    if invitation_dict['prewedding_photos']:
        try:
            prewedding_photos = json.loads(invitation_dict['prewedding_photos'])
            print(f"DEBUG PHOTOS: Found {len(prewedding_photos)} prewedding photos")
            for i, photo in enumerate(prewedding_photos):
                if isinstance(photo, dict):
                    print(f"  Photo {i+1}: {photo.get('filename', 'no filename')} ({photo.get('orientation', 'no orientation')})")
                else:
                    print(f"  Photo {i+1}: {photo} (old format)")
        except Exception as e:
            print(f"DEBUG PHOTOS: Error parsing prewedding photos: {str(e)}")
            prewedding_photos = []
    else:
        print("DEBUG PHOTOS: No prewedding photos data found")

    # Debug template selection
    print(f"DEBUG: Template ID: {invitation_dict.get('template_id')}")
    print(f"DEBUG: Template file from DB: {invitation_dict.get('template_file')}")

    # Get template file name
    template_file = invitation_dict.get('template_file')

    # If no template file specified, show error
    if not template_file:
        print(f"ERROR: No template file specified for invitation {invitation_dict.get('id')}")
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

    # Check template file in Documents folder first, then fallback to app folder
    documents_template_path = os.path.join(app.config['WEDDING_FOLDER'], template_file)
    app_template_path = os.path.join('templates/wedding_templates', template_file)

    template_found = False
    template_render_path = ''

    if os.path.exists(documents_template_path):
        # Load template from Documents folder
        with open(documents_template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()

        # Render template string directly
        try:
            return render_template_string(template_content,
                                       invitation=invitation_dict,
                                       guests=guests,
                                       prewedding_photos=prewedding_photos)
        except Exception as e:
            print(f"ERROR: Failed to render template from Documents: {str(e)}")

    elif os.path.exists(app_template_path):
        # Fallback to app folder
        template_render_path = f'wedding_templates/{template_file}'
        template_found = True
    else:
        print(f"ERROR: Template file not found in either location")
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Template Tidak Ditemukan</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 2rem; }
                .error-container { max-width: 600px; margin: 0 auto; }
                .error-icon { font-size: 4rem; color: #e74c3c; margin-bottom: 1rem; }
                h1 { color: #e74c3c; }
                p { color: #666; line-height: 1.6; }
                .details { background: #f8f9fa; padding: 1rem; border-radius: 5px; margin-top: 1rem; }
            </style>
        </head>
        <body>
            <div class="error-container">
                <div class="error-icon">📄</div>
                <h1>Template File Not Found</h1>
                <p>Template file tidak ditemukan di Documents maupun folder aplikasi.</p>
                <div class="details">
                    <p><strong>Template file:</strong> {{ template_file }}</p>
                    <p><strong>Documents path:</strong> {{ documents_path }}</p>
                    <p><strong>App path:</strong> {{ app_path }}</p>
                </div>
            </div>
        </body>
        </html>
        """, template_file=template_file, documents_path=documents_template_path, app_path=app_template_path), 404

    if template_found:
        try:
            print(f"DEBUG: Attempting to render template from app folder: {template_render_path}")
            return render_template(template_render_path,
                                 invitation=invitation_dict,
                                 guests=guests,
                                 prewedding_photos=prewedding_photos)
        except Exception as e:
            print(f"ERROR: Failed to render template {template_render_path}: {str(e)}")
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
                        <p>An error occurred while loading the wedding invitation template.</p>
                        <div class="details">
                            <p><strong>Template:</strong> {{ template_file }}</p>
                            <p><strong>Error:</strong> {{ error }}</p>
                            <p><strong>Couple:</strong> {{ couple_name }}</p>
                        </div>
                    </div>
                </body>
                </html>
                """, template_file=template_render_path, error=str(e), couple_name=invitation_dict.get('couple_name', 'Unknown')), 500

@app.route('/edit-wedding-invitation/<int:id>')
@require_auth
def edit_wedding_invitation(id):
    """Edit wedding invitation (placeholder)"""
    flash('Fitur edit undangan sedang dalam pengembangan', 'info')
    return redirect(url_for('wedding_invitations'))

@app.route('/manage-guests/<int:invitation_id>')
@require_auth
def manage_guests(invitation_id):
    """Manage wedding guests (placeholder)"""
    flash('Fitur kelola tamu sedang dalam pengembangan', 'info')
    return redirect(url_for('wedding_invitations'))

@app.route('/invitation-analytics/<int:invitation_id>')
@require_auth
def invitation_analytics(invitation_id):
    """View invitation analytics (placeholder)"""
    flash('Fitur analytics sedang dalam pengembangan', 'info')
    return redirect(url_for('wedding_invitations'))

@app.route('/toggle-invitation-status/<int:invitation_id>')
@require_auth
def toggle_invitation_status(invitation_id):
    """Toggle invitation active status"""
    conn = get_db()
    invitation = conn.execute(
        'SELECT * FROM wedding_invitations WHERE id = ? AND user_id = ?',
        (invitation_id, session['user_id'])
    ).fetchone()

    if not invitation:
        flash('Undangan tidak ditemukan!', 'error')
        return redirect(url_for('wedding_invitations'))

    new_status = 0 if invitation['is_active'] else 1
    conn.execute(
        'UPDATE wedding_invitations SET is_active = ? WHERE id = ?',
        (new_status, invitation_id)
    )
    conn.commit()
    conn.close()

    status_text = 'diaktifkan' if new_status else 'dinonaktifkan'
    flash(f'Undangan berhasil {status_text}!', 'success')
    return redirect(url_for('wedding_invitations'))

@app.route('/delete-invitation/<int:invitation_id>')
@require_auth
def delete_invitation(invitation_id):
    """Delete wedding invitation"""
    conn = get_db()
    invitation = conn.execute(
        'SELECT * FROM wedding_invitations WHERE id = ? AND user_id = ?',
        (invitation_id, session['user_id'])
    ).fetchone()

    if not invitation:
        flash('Undangan tidak ditemukan!', 'error')
        return redirect(url_for('wedding_invitations'))

    # Delete associated guests first
    conn.execute('DELETE FROM wedding_guests WHERE invitation_id = ?', (invitation_id,))
    # Delete invitation
    conn.execute('DELETE FROM wedding_invitations WHERE id = ?', (invitation_id,))
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
    conn.execute('''
        INSERT INTO wedding_guests (invitation_id, name, phone, email, attendance, guest_count, message, wishes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (invitation_id, name, phone, email, attendance, guest_count, message, wishes))
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
        admin = conn.execute('SELECT * FROM admin WHERE username = ?', (username,)).fetchone()
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

@app.route('/admin/dashboard')
@require_admin
def admin_dashboard():
    conn = get_db()

    total_users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    total_invitations = conn.execute('SELECT COUNT(*) FROM wedding_invitations').fetchone()[0]
    total_cv_templates = conn.execute('SELECT COUNT(*) FROM cv_templates').fetchone()[0]
    total_wedding_templates = conn.execute('SELECT COUNT(*) FROM wedding_templates').fetchone()[0]
    total_orders = conn.execute('SELECT COUNT(*) FROM orders').fetchone()[0]
    pending_orders = conn.execute('SELECT COUNT(*) FROM orders WHERE status = "Pending"').fetchone()[0]

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
        action = request.form.get('action', 'add')

        if action == 'add':
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
                    file_path = os.path.join(app.config['TEMPLATES_FOLDER'], filename)
                    file.save(file_path)
                    template_file = filename

            if 'preview_image' in request.files:
                file = request.files['preview_image']
                if file.filename != '':
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['TEMPLATES_FOLDER'], filename)
                    file.save(file_path)
                    preview_image = filename

            conn = get_db()
            conn.execute('''
                INSERT INTO cv_templates (name, description, category, template_file, preview_image, color_scheme, animations, is_premium)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, description, category, template_file, preview_image, color_scheme, animations, is_premium))
            conn.commit()
            conn.close()

            flash('Template CV berhasil ditambahkan!', 'success')
            return redirect(url_for('admin_cv_templates'))

        elif action == 'edit':
            template_id = request.form['template_id']
            name = request.form['name']
            description = request.form['description']
            category = request.form['category']
            color_scheme = request.form['color_scheme']
            animations = request.form['animations']
            is_premium = 1 if request.form.get('is_premium') else 0

            # Handle file uploads (optional update)
            template_file = request.form.get('current_template_file', '')
            preview_image = request.form.get('current_preview_image', '')

            if 'template_file' in request.files:
                file = request.files['template_file']
                if file.filename != '':
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['TEMPLATES_FOLDER'], filename)
                    file.save(file_path)
                    template_file = filename

            if 'preview_image' in request.files:
                file = request.files['preview_image']
                if file.filename != '':
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['TEMPLATES_FOLDER'], filename)
                    file.save(file_path)
                    preview_image = filename

            conn = get_db()
            conn.execute('''
                UPDATE cv_templates
                SET name = ?, description = ?, category = ?, template_file = ?, preview_image = ?,
                    color_scheme = ?, animations = ?, is_premium = ?
                WHERE id = ?
            ''', (name, description, category, template_file, preview_image, color_scheme, animations, is_premium, template_id))
            conn.commit()
            conn.close()

            flash('Template CV berhasil diperbarui!', 'success')
            return redirect(url_for('admin_cv_templates'))

        elif action == 'delete':
            template_id = request.form['template_id']
            conn = get_db()
            conn.execute('DELETE FROM cv_templates WHERE id = ?', (template_id,))
            conn.commit()
            conn.close()
            flash('Template CV berhasil dihapus!', 'success')
            return redirect(url_for('admin_cv_templates'))

    conn = get_db()
    templates = conn.execute('SELECT * FROM cv_templates ORDER BY created_at DESC').fetchall()
    conn.close()

    return render_template('admin/cv_templates.html', templates=templates)

@app.route('/admin/download-base-template')
@require_admin
def download_base_template():
    """Download base template for theme development"""
    try:
        template_path = os.path.join('templates', 'admin', 'base_template.html')
        return send_file(template_path, as_attachment=True, download_name='wedding_base_template.html')
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
    template = conn.execute('SELECT * FROM wedding_templates WHERE id = ?', (template_id,)).fetchone()

    if not template:
        flash('Template tidak ditemukan!', 'error')
        return redirect(url_for('admin_wedding_templates'))

    # Generate thumbnail
    thumbnail_filename = generate_thumbnail_from_template(
        template['id'],
        template['name'],
        template['color_scheme'],
        template['template_file']   # tambahkan ini
    )


    if thumbnail_filename:
        # Update database with new thumbnail
        conn.execute('UPDATE wedding_templates SET preview_image = ? WHERE id = ?',
                    (thumbnail_filename, template_id))
        conn.commit()
        flash(f'Thumbnail berhasil digenerate untuk template {template["name"]}!', 'success')
    else:
        flash('Gagal generate thumbnail!', 'error')

    conn.close()
    return redirect(url_for('admin_wedding_templates'))

@app.route('/admin/demo-template/<int:template_id>')
@require_admin
def admin_demo_template(template_id):
    """Admin demo route for wedding templates"""
    return preview_wedding_template(template_id)

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
            template['template_file']   # tambahkan ini
        )

        if thumbnail_filename:
            conn.execute('UPDATE wedding_templates SET preview_image = ? WHERE id = ?',
                        (thumbnail_filename, template['id']))
            success_count += 1

    conn.commit()
    conn.close()

    flash(f'Berhasil generate {success_count} dari {total_count} thumbnails!', 'success')
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
        thumbnail_path = os.path.join('static/images/wedding_templates', thumbnail_filename)
        os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)

        image.convert("RGB").save(thumbnail_path, "JPEG", quality=85)

        driver.quit()
        return thumbnail_filename

    except Exception as e:
        print(f"[Thumbnail Error] Selenium failed for template {template_file} (ID {template_id}): {e}")
        if 'driver' in locals():
            try:
                driver.quit()
            except:
                pass

        # Fallback to simple image generation
        return generate_simple_wedding_thumbnail(template_id, template_name, color_scheme)

def generate_simple_wedding_thumbnail(template_id, template_name, color_scheme):
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
        draw.rectangle([0, height-40, width, height], fill=primary_color)

        # Center heart or rings
        center_x, center_y = width//2, height//2

        # Draw wedding rings or heart
        if random.choice([True, False]):
            # Draw heart shape (simplified)
            heart_size = 30
            draw.ellipse([center_x-heart_size, center_y-15, center_x, center_y+15], fill=accent_color)
            draw.ellipse([center_x, center_y-15, center_x+heart_size, center_y+15], fill=accent_color)
        else:
            # Draw wedding rings
            ring_size = 25
            draw.ellipse([center_x-40, center_y-ring_size, center_x-40+ring_size*2, center_y+ring_size],
                        outline=accent_color, width=4)
            draw.ellipse([center_x+15, center_y-ring_size, center_x+15+ring_size*2, center_y+ring_size],
                        outline=accent_color, width=4)

        # Decorative elements
        for i in range(3):
            y_pos = 80 + (i * 30)
            draw.rectangle([50, y_pos, width-50, y_pos+8], fill=primary_color)
            draw.rectangle([80, y_pos+15, width-80, y_pos+20], fill=accent_color)

        # Template name indicator
        name_width = min(len(template_name) * 8, width-20)
        draw.rectangle([10, height-30, 10 + name_width, height-20], fill=accent_color)

        # Save thumbnail
        timestamp = str(int(datetime.now().timestamp()))
        thumbnail_filename = f"{timestamp}_simple_template_{template_id}_thumbnail.jpg"
        thumbnail_path = os.path.join('static/images/wedding_templates', thumbnail_filename)
        os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)

        img.save(thumbnail_path, "JPEG", quality=85)
        return thumbnail_filename

    except Exception as e:
        print(f"[Simple Thumbnail Error] Template {template_name} (ID {template_id}): {e}")
        return None

@app.route('/admin/generate-cv-thumbnail/<int:template_id>')
@require_admin
def generate_cv_template_thumbnail(template_id):
    """Generate thumbnail for a specific CV template"""
    conn = get_db()
    template = conn.execute('SELECT * FROM cv_templates WHERE id = ?', (template_id,)).fetchone()

    if not template:
        flash('Template tidak ditemukan!', 'error')
        return redirect(url_for('admin_cv_templates'))

    # Generate thumbnail for CV with category info
    thumbnail_filename = generate_cv_thumbnail_simple(
        template['id'],
        template['name'],
        template['color_scheme'],
        template['category']
    )

    if thumbnail_filename:
        # Update database with new thumbnail
        conn.execute('UPDATE cv_templates SET preview_image = ? WHERE id = ?',
                    (thumbnail_filename, template_id))
        conn.commit()
        flash(f'Thumbnail berhasil digenerate untuk template {template["name"]}!', 'success')
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
            template['id'],
            template['name'],
            template['color_scheme'],
            template['category']
        )

        if thumbnail_filename:
            conn.execute('UPDATE cv_templates SET preview_image = ? WHERE id = ?',
                        (thumbnail_filename, template['id']))
            success_count += 1

    conn.commit()
    conn.close()

    flash(f'Berhasil generate {success_count} dari {total_count} CV thumbnails!', 'success')
    return redirect(url_for('admin_cv_templates'))

@app.route('/admin/wedding-templates', methods=['GET', 'POST'])
@require_admin
def admin_wedding_templates():
    if request.method == 'POST':
        action = request.form.get('action', 'add')

        if action == 'add':
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
                    file_path = os.path.join(app.config['WEDDING_FOLDER'], filename)
                    file.save(file_path)
                    template_file = filename

            # save background music
            if 'background_music' in request.files:
                file = request.files['background_music']
                if file.filename != '':
                    filename = secure_filename(file.filename)
                    timestamp = str(int(datetime.now().timestamp()))
                    filename = f"{timestamp}_{filename}"
                    file_path = os.path.join(app.config['MUSIC_FOLDER'], filename)
                    file.save(file_path)
                    background_music = filename

            conn = get_db()
            conn.execute('''
                INSERT INTO wedding_templates
                (name, description, category, template_file, preview_image, color_scheme, animations, background_music, ornaments, is_premium, price)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, description, category, template_file, '', color_scheme, animations, background_music, ornaments, is_premium, price))
            conn.commit()
            conn.close()

            flash('Template wedding berhasil ditambahkan!', 'success')

        elif action == 'edit':
            template_id = request.form['template_id']
            name = request.form['name']
            description = request.form['description']
            category = request.form['category']
            color_scheme = request.form['color_scheme']
            animations = request.form['animations']
            ornaments = request.form['ornaments']
            is_premium = 1 if request.form.get('is_premium') else 0
            price = int(request.form.get('price', 0))

            # Handle file uploads (optional update)
            template_file = request.form.get('current_template_file', '')
            background_music = request.form.get('current_background_music', '')

            if 'template_file' in request.files:
                file = request.files['template_file']
                if file.filename != '':
                    filename = secure_filename(file.filename)
                    timestamp = str(int(datetime.now().timestamp()))
                    filename = f"{timestamp}_{filename}"
                    file_path = os.path.join(app.config['WEDDING_FOLDER'], filename)
                    file.save(file_path)
                    template_file = filename

            if 'background_music' in request.files:
                file = request.files['background_music']
                if file.filename != '':
                    filename = secure_filename(file.filename)
                    timestamp = str(int(datetime.now().timestamp()))
                    filename = f"{timestamp}_{filename}"
                    file_path = os.path.join(app.config['MUSIC_FOLDER'], filename)
                    file.save(file_path)
                    background_music = filename

            conn = get_db()
            conn.execute('''
                UPDATE wedding_templates
                SET name = ?, description = ?, category = ?, template_file = ?, color_scheme = ?,
                    animations = ?, background_music = ?, ornaments = ?, is_premium = ?, price = ?
                WHERE id = ?
            ''', (name, description, category, template_file, color_scheme, animations, background_music, ornaments, is_premium, price, template_id))
            conn.commit()
            conn.close()

            flash('Template wedding berhasil diperbarui!', 'success')
            return redirect(url_for('admin_wedding_templates'))

        elif action == 'delete':
            template_id = request.form['template_id']
            conn = get_db()
            conn.execute('DELETE FROM wedding_templates WHERE id = ?', (template_id,))
            conn.commit()
            conn.close()
            flash('Template wedding berhasil dihapus!', 'success')
            return redirect(url_for('admin_wedding_templates'))

        return redirect(url_for('admin_wedding_templates'))

    conn = get_db()
    templates = conn.execute('SELECT * FROM wedding_templates ORDER BY created_at DESC').fetchall()
    conn.close()

    return render_template('admin/wedding_templates.html', templates=templates)

@app.route('/admin/users')
@require_admin
def admin_users():
    conn = get_db()
    users = conn.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()
    conn.close()

    return render_template('admin/users.html', users=users)

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

    return render_template('admin/wedding_invitations.html', invitations=invitations)

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
    conn.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
    conn.commit()
    conn.close()

    flash('Status pesanan berhasil diperbarui!', 'success')
    return redirect(request.referrer or url_for('admin_orders'))

@app.route('/view-order/<int:order_id>')
@require_admin
def view_order(order_id):
    conn = get_db()
    order = conn.execute('''
        SELECT o.*, u.name as user_name
        FROM orders o
        LEFT JOIN users u ON o.user_id = u.id
        WHERE o.id = ?
    ''', (order_id,)).fetchone()
    conn.close()

    if not order:
        flash('Pesanan tidak ditemukan!', 'error')
        return redirect(url_for('admin_orders'))

    return render_template('admin/view_order.html', order=order)

@app.route('/download-file/<int:order_id>')
@require_admin
def download_file(order_id):
    conn = get_db()
    order = conn.execute('SELECT file_path FROM orders WHERE id = ?', (order_id,)).fetchone()
    conn.close()

    if not order or not order['file_path']:
        flash('File tidak ditemukan!', 'error')
        return redirect(url_for('admin_orders'))

    try:
        return send_file(os.path.join(app.config['UPLOAD_FOLDER'], order['file_path']), as_attachment=True)
    except FileNotFoundError:
        flash('File tidak ditemukan di server!', 'error')
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
        all_invitations = conn.execute('SELECT * FROM wedding_invitations').fetchall()

        # Cek user yang sedang login
        current_user_invitations = []
        if 'user_id' in session:
            current_user_invitations = conn.execute(
                'SELECT * FROM wedding_invitations WHERE user_id = ?',
                (session['user_id'],)
            ).fetchall()

        # Cek semua template wedding
        all_templates = conn.execute('SELECT id, name, template_file FROM wedding_templates').fetchall()

        conn.close()

        debug_info = {
            'user_id': session.get('user_id', 'Not logged in'),
            'total_invitations': len(all_invitations),
            'user_invitations': len(current_user_invitations),
            'all_invitations': [dict(inv) for inv in all_invitations],
            'user_invitations_data': [dict(inv) for inv in current_user_invitations],
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
            cursor = conn.execute('''
                INSERT INTO wedding_invitations
                (user_id, couple_name, bride_name, bride_father, bride_mother, groom_name, groom_father, groom_mother, venue_address, template_id, invitation_link, guest_limit)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (1, 'Test Couple', 'Test Bride', 'Test Father', 'Test Mother', 'Test Groom', 'Test Father 2', 'Test Mother 2', 'Test Venue', 1, 'test-link-123', 100))

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
from datetime import datetime

# --- fungsi database ---
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = [dict((cur.description[idx][0], value)
          for idx, value in enumerate(row)) for row in cur.fetchall()]
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route("/preview-thumbnail/<int:template_id>")
def preview_thumbnail(template_id):
    # ambil data template dari DB
    template = query_db(
        "SELECT * FROM wedding_templates WHERE id = ?",
        [template_id],
        one=True
    )
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
        'venue_address': 'Jl. Pasir Wangi, Gudangkahuripan, Kec. Lembang, Kabupaten Bandung Barat, Jawa Barat 40391',

        # Multi-venue fields
        'akad_date': datetime.strptime('2027-07-30', '%Y-%m-%d'),
        'akad_time': '14:00',
        'akad_venue_name': 'Masjid Al-Ikhlas',
        'akad_venue_address': 'Jl. Raya Lembang No. 123, Lembang, Bandung Barat',

        'resepsi_date': datetime.strptime('2027-07-30', '%Y-%m-%d'),
        'resepsi_time': '19:00',
        'resepsi_venue_name': 'Trizara Resorts Glamping Lembang',
        'resepsi_venue_address': 'Jl. Pasir Wangi, Gudangkahuripan, Kec. Lembang, Kabupaten Bandung Barat, Jawa Barat 40391',

        # Optional family events
        'bride_event_date': datetime.strptime('2027-07-29', '%Y-%m-%d'),
        'bride_event_time': '16:00',
        'bride_event_venue_name': 'Kediaman Keluarga Mempelai Wanita',
        'bride_event_venue_address': 'Jl. Keluarga No. 45, Bandung',

        'groom_event_date': datetime.strptime('2027-07-31', '%Y-%m-%d'),
        'groom_event_time': '18:00',
        'groom_event_venue_name': 'Kediaman Keluarga Mempelai Pria',
        'groom_event_venue_address': 'Jl. Keluarga Pria No. 67, Cimahi',

        'custom_message': 'Dengan penuh kebahagiaan, kami mengundang Anda',
        'color_scheme': template['color_scheme'],
        'template_name': template['name'],

        # field tambahan biar template lain tidak error
        'bank_name': 'MANDIRI',
        'bank_account': '1320026475575',
        'account_holder': 'Fajar Julyana',
        'qris_code': '',
        'guest_limit': 200,
        'invitation_link': 'preview-sample',
        'qr_code': '',
        'background_music': '',
        'ornaments': '',
    }

    # pastikan prefix folder benar
    template_file = template['template_file']
    if template_file and not template_file.startswith("wedding_templates/"):
        template_file = f"wedding_templates/{template_file}"

    print(f"DEBUG THUMBNAIL: Attempting to render template: {template_file}")

    try:
        # render template HTML
        return render_template(
            template_file,
            invitation=sample_invitation,
            guests=[],
            prewedding_photos=[]
        )
    except Exception as e:
        print(f"ERROR THUMBNAIL: Failed to render template {template_file}: {str(e)}")
        # Try without prefix
        try:
            return render_template(
                template['template_file'],
                invitation=sample_invitation,
                guests=[],
                prewedding_photos=[]
            )
        except Exception as e2:
            print(f"ERROR THUMBNAIL: Also failed without prefix: {str(e2)}")
            # Use fallback
            return render_template(
                'wedding_invitation_view.html',
                invitation=sample_invitation,
                guests=[],
                prewedding_photos=[]
            )
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
        conn.execute('''
            INSERT INTO chat_messages
            (sender_type, sender_id, sender_name, sender_email, message, room_type, room_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (sender_type, sender_id, sender_name, sender_email, message, room_type, room_id))
        conn.commit()
        conn.close()

        # Broadcast ke semua user di room
        emit('receive_message', {
            'message': message,
            'sender_name': sender_name,
            'sender_type': sender_type,
            'timestamp': datetime.now().strftime('%H:%M'),
            'date': datetime.now().strftime('%Y-%m-%d')
        }, room=room)

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
    messages = conn.execute('''
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


import os
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

server_thread = None
gui_window = None

# ---------------- Logging ----------------
def log_error(e):
    with open("error_log.txt", "a", encoding="utf-8") as f:
        f.write(traceback.format_exc() + "\n")

# ---------------- Flask Runner ----------------
def run_flask():
    try:
        init_db()

        # Buka browser otomatis setelah delay kecil
        def open_browser():
            time.sleep(2)
            url = "https://fajarmandiri.store"
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

        threading.Thread(target=open_browser, daemon=True).start()

        # Try SocketIO first, fallback to regular Flask if SocketIO fails
        try:
            socketio.run(
                app,
                host="0.0.0.0",
                port=5001,
                debug=False,
                use_reloader=False,
                allow_unsafe_werkzeug=True
            )
        except Exception as e:
            print(f"SocketIO failed to run: {str(e)}")
            print("Falling back to regular Flask server...")
            app.run(
                host="0.0.0.0",
                port=5001,
                debug=False,
                use_reloader=False
            )

    except Exception as e:
        log_error(e)

# ---------------- Service Control ----------------
def start_service(icon=None, item=None):
    global server_thread
    if server_thread is None or not server_thread.is_alive():
        server_thread = threading.Thread(target=run_flask, daemon=True)
        server_thread.start()

def stop_service(icon=None, item=None):
    try:
        if icon:
            icon.stop()
    except:
        pass

    # Kill child processes (Flask reloader, etc.)
    parent = psutil.Process(os.getpid())
    for child in parent.children(recursive=True):
        try:
            child.kill()
        except:
            pass

    os._exit(0)

# ---------------- Tray Icon ----------------
def get_tray_icon():
    try:
        # Jika dibundle ke exe, PyInstaller simpan resource di sys._MEIPASS
        base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_path, "icon.ico")

        if os.path.exists(icon_path):
            return Image.open(icon_path)
        else:
            # fallback: gambar bulat biru
            image = Image.new("RGB", (64, 64), (0, 0, 0, 0))
            dc = ImageDraw.Draw(image)
            dc.ellipse((8, 8, 56, 56), fill="blue")
            return image
    except Exception as e:
        log_error(e)
        # fallback kalau gagal
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
        log_error(e)

# ---------------- Main ----------------
if __name__ == "__main__":
    start_service()
    threading.Thread(target=run_tray, daemon=True).start()

    # Loop biar process tetap hidup
    while True:
        time.sleep(1)