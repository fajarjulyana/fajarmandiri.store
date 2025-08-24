
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, jsonify
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

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['TEMPLATES_FOLDER'] = 'cv_templates'
app.config['WEDDING_FOLDER'] = 'wedding_invitations'
app.config['MUSIC_FOLDER'] = 'music'
app.config['PREWEDDING_FOLDER'] = 'prewedding_photos'

# Create necessary directories
for folder in [app.config['UPLOAD_FOLDER'], app.config['TEMPLATES_FOLDER'], 
               app.config['WEDDING_FOLDER'], app.config['MUSIC_FOLDER'], 
               app.config['PREWEDDING_FOLDER']]:
    if not os.path.exists(folder):
        os.makedirs(folder)

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

def reset_database():
    """Reset database dan buat ulang dengan struktur yang benar"""
    try:
        # Backup existing database
        if os.path.exists('wedding_app.db'):
            import shutil
            shutil.copy('wedding_app.db', f'wedding_app_backup_{int(datetime.now().timestamp())}.db')
        
        # Hapus database lama
        if os.path.exists('wedding_app.db'):
            os.remove('wedding_app.db')
            
        print("Database lama dihapus, membuat database baru...")
        init_db()
        print("Database baru berhasil dibuat!")
        
    except Exception as e:
        print(f"Error reset database: {str(e)}")

def init_db():
    conn = sqlite3.connect('wedding_app.db')
    c = conn.cursor()
    
    print("Membuat struktur database...")
    
    # Users table for both Google OAuth and manual registration
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        google_id TEXT,
        email TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        password TEXT,
        picture TEXT,
        is_premium BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Orders table for printing services
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
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
    c.execute('''CREATE TABLE IF NOT EXISTS cv_templates (
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
    
    # Wedding invitation templates table
    c.execute('''CREATE TABLE IF NOT EXISTS wedding_templates (
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
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Wedding invitations table - STRUKTUR DIPERBAIKI
    c.execute('''CREATE TABLE IF NOT EXISTS wedding_invitations (
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
    c.execute('''CREATE TABLE IF NOT EXISTS wedding_guests (
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
    c.execute('''CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    )''')
    
    # Insert default admin if not exists
    c.execute('SELECT COUNT(*) FROM admin WHERE username = ?', ('admin',))
    if c.fetchone()[0] == 0:
        hashed_password = generate_password_hash('admin123')
        c.execute('INSERT INTO admin (username, password) VALUES (?, ?)', ('admin', hashed_password))
        print("Admin default dibuat: username=admin, password=admin123")
    
    # Insert default wedding templates
    default_wedding_templates = [
        ('Classic Elegant', 'Elegant classic wedding theme with gold ornaments', 'elegant', 'wedding_templates/classic_elegant.html', 'classic_preview.jpg', 'gold-cream', 'gentle,elegant', 'wedding_classic.mp3', 'classic_ornaments', 0),
        ('Modern Minimalist', 'Clean and modern wedding invitation', 'modern', 'wedding_templates/modern_minimal.html', 'modern_preview.jpg', 'blue-white', 'minimal,clean', 'wedding_modern.mp3', 'geometric_lines', 0),
        ('Royal Gold', 'Luxurious royal theme with gold elements', 'luxury', 'wedding_templates/royal_gold.html', 'royal_preview.jpg', 'gold-black', 'luxury,elegant', 'wedding_royal.mp3', 'crown_elements', 1),
        ('Floral Garden', 'Beautiful floral wedding theme', 'floral', 'wedding_templates/floral_garden.html', 'floral_preview.jpg', 'pink-green', 'natural,soft', 'wedding_garden.mp3', 'flower_elements', 0),
        ('Beach Romance', 'Romantic beach wedding theme', 'beach', 'wedding_templates/beach_romance.html', 'beach_preview.jpg', 'blue-sand', 'wave,gentle', 'wedding_beach.mp3', 'ocean_elements', 0),
        ('Vintage Romance', 'Vintage style romantic invitation', 'vintage', 'wedding_templates/vintage_romance.html', 'vintage_preview.jpg', 'sepia-brown', 'vintage,classic', 'wedding_vintage.mp3', 'antique_elements', 1),
        ('Anime Sakura', 'Japanese anime style with cherry blossoms', 'anime', 'wedding_templates/anime_sakura.html', 'anime_preview.jpg', 'pink-purple', 'anime,sakura', 'anime_wedding.mp3', 'sakura_elements', 1),
        ('Rustic Charm', 'Rustic countryside wedding theme', 'rustic', 'rustic_charm.html', 'rustic_preview.jpg', 'brown-green', 'fadeIn,slideDown', 'wedding_rustic.mp3', 'wood_ornaments', 0),
        ('Art Deco', 'Sophisticated art deco design', 'artdeco', 'art_deco.html', 'artdeco_preview.jpg', 'gold-black', 'slideUp,rotateIn', 'wedding_deco.mp3', 'geometric_gold', 1),
        ('Botanical Luxury', 'Luxurious botanical wedding theme', 'botanical', 'botanical_luxury.html', 'botanical_preview.jpg', 'green-gold', 'fadeIn,bounceIn', 'wedding_botanical.mp3', 'botanical_gold', 1)
    ]
    
    for template in default_wedding_templates:
        c.execute('''INSERT OR IGNORE INTO wedding_templates 
                     (name, description, category, template_file, preview_image, color_scheme, animations, background_music, ornaments, is_premium) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', template)
    
    # Insert default CV templates
    default_cv_templates = [
        ('Modern Professional', 'Clean and modern design perfect for corporate jobs', 'corporate', 'modern_pro.html', 'modern_pro_preview.jpg', 0, 'blue', 'fadeIn'),
        ('Creative Designer', 'Colorful and creative template for designers', 'creative', 'creative.html', 'creative_preview.jpg', 0, 'rainbow', 'slideUp'),
        ('Executive Elite', 'Premium template for senior positions', 'executive', 'executive.html', 'executive_preview.jpg', 1, 'gold-black', 'fadeIn,slideDown'),
        ('Tech Specialist', 'Perfect for IT and tech professionals', 'tech', 'tech.html', 'tech_preview.jpg', 0, 'blue-gray', 'slideLeft'),
        ('Minimalist Pro', 'Simple and elegant minimalist design', 'minimal', 'minimalist.html', 'minimalist_preview.jpg', 0, 'gray', 'fadeIn'),
        ('Healthcare Professional', 'Professional template for medical professionals', 'medical', 'healthcare.html', 'healthcare_preview.jpg', 1, 'blue-white', 'slideUp'),
        ('Sales & Marketing', 'Dynamic template for sales professionals', 'sales', 'sales.html', 'sales_preview.jpg', 1, 'red-orange', 'bounceIn'),
        ('Academic Scholar', 'Ideal for researchers and academics', 'academic', 'academic.html', 'academic_preview.jpg', 0, 'navy-gold', 'fadeIn'),
        ('Startup Innovator', 'Modern template for startup enthusiasts', 'startup', 'startup.html', 'startup_preview.jpg', 1, 'purple-cyan', 'slideDown'),
        ('International Standard', 'Global standard professional template', 'international', 'international.html', 'international_preview.jpg', 1, 'black-gold', 'fadeIn,rotateIn')
    ]
    
    for template in default_cv_templates:
        c.execute('''INSERT OR IGNORE INTO cv_templates 
                     (name, description, category, template_file, preview_image, is_premium, color_scheme, animations) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', template)
    
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect('wedding_app.db')
    conn.row_factory = sqlite3.Row
    return conn

def generate_thumbnail_from_template(template_id, template_name, color_scheme):
    """Generate thumbnail from wedding template"""
    try:
        # Setup Chrome options for headless browsing
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1200,800")
        
        # Initialize webdriver
        driver = webdriver.Chrome(options=chrome_options)
        
        # Create sample data for preview
        sample_data = {
            'bride_name': 'Sarah',
            'groom_name': 'David',
            'couple_name': 'Sarah & David',
            'wedding_date': '2024-12-25',
            'wedding_time': '14:00',
            'venue_name': 'Grand Ballroom',
            'venue_address': 'Jl. Sample Street No. 123',
            'bride_father': 'Mr. John',
            'bride_mother': 'Mrs. Jane',
            'groom_father': 'Mr. Robert',
            'groom_mother': 'Mrs. Linda',
            'custom_message': 'Dengan penuh kebahagiaan, kami mengundang Anda',
            'color_scheme': color_scheme,
            'template_name': template_name
        }
        
        # Create temporary HTML file with sample data
        temp_html = f"""
        <!DOCTYPE html>
        <html lang="id">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Wedding Invitation Preview</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
            <style>
                body {{ 
                    font-family: 'Georgia', serif;
                    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                    margin: 0;
                    padding: 20px;
                }}
                .invitation-container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 20px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px 20px;
                    text-align: center;
                }}
                .couple-names {{
                    font-size: 2.5rem;
                    font-weight: bold;
                    margin-bottom: 20px;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                }}
                .wedding-date {{
                    font-size: 1.2rem;
                    opacity: 0.9;
                }}
                .content {{
                    padding: 40px;
                }}
                .section {{
                    margin-bottom: 30px;
                    text-align: center;
                }}
                .venue-info {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 10px;
                    margin: 20px 0;
                }}
                .ornament {{
                    font-size: 2rem;
                    color: #667eea;
                    margin: 10px 0;
                }}
            </style>
        </head>
        <body>
            <div class="invitation-container">
                <div class="header">
                    <div class="ornament">
                        <i class="fas fa-heart"></i> <i class="fas fa-ring"></i> <i class="fas fa-heart"></i>
                    </div>
                    <h1 class="couple-names">{sample_data['couple_name']}</h1>
                    <div class="wedding-date">
                        <i class="far fa-calendar-alt me-2"></i>
                        25 Desember 2024 | 14:00 WIB
                    </div>
                </div>
                
                <div class="content">
                    <div class="section">
                        <h3>Dengan memohon rahmat dan ridho Allah SWT</h3>
                        <p>Kami bermaksud mengundang Bapak/Ibu/Saudara/i untuk hadir di acara pernikahan kami</p>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-6">
                            <div class="section">
                                <h4>Mempelai Wanita</h4>
                                <h5>{sample_data['bride_name']}</h5>
                                <p>Putri dari<br>
                                Bpk. {sample_data['bride_father']} & Ibu {sample_data['bride_mother']}</p>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="section">
                                <h4>Mempelai Pria</h4>
                                <h5>{sample_data['groom_name']}</h5>
                                <p>Putra dari<br>
                                Bpk. {sample_data['groom_father']} & Ibu {sample_data['groom_mother']}</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="venue-info">
                        <h4><i class="fas fa-map-marker-alt me-2"></i>Lokasi Acara</h4>
                        <h5>{sample_data['venue_name']}</h5>
                        <p>{sample_data['venue_address']}</p>
                    </div>
                    
                    <div class="section">
                        <div class="ornament">
                            <i class="fas fa-heart"></i>
                        </div>
                        <p>Merupakan suatu kehormatan dan kebahagiaan bagi kami apabila Bapak/Ibu/Saudara/i berkenan hadir untuk memberikan doa restu kepada kedua mempelai.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Save temporary HTML file
        temp_filename = f"temp_preview_{template_id}.html"
        with open(temp_filename, 'w', encoding='utf-8') as f:
            f.write(temp_html)
        
        # Load the page
        file_url = f"file://{os.path.abspath(temp_filename)}"
        driver.get(file_url)
        
        # Wait for page to load
        time.sleep(3)
        
        # Take screenshot
        screenshot = driver.get_screenshot_as_png()
        
        # Process image with PIL
        image = Image.open(BytesIO(screenshot))
        
        # Resize to thumbnail size (400x300)
        image.thumbnail((400, 300), Image.Resampling.LANCZOS)
        
        # Save thumbnail
        timestamp = str(int(datetime.now().timestamp()))
        thumbnail_filename = f"{timestamp}_template_{template_id}_thumbnail.jpg"
        thumbnail_path = os.path.join('static/images/wedding_templates', thumbnail_filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
        
        # Save as JPEG
        rgb_image = image.convert('RGB')
        rgb_image.save(thumbnail_path, 'JPEG', quality=85)
        
        # Cleanup
        driver.quit()
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        
        return thumbnail_filename
        
    except Exception as e:
        print(f"Error generating thumbnail: {str(e)}")
        if 'driver' in locals():
            driver.quit()
        if 'temp_filename' in locals() and os.path.exists(temp_filename):
            os.remove(temp_filename)
        return None

def require_auth(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu', 'warning')
            return redirect(url_for('login'))
        # Pastikan bukan admin yang mencoba akses user area
        if 'admin' in session:
            flash('Admin tidak dapat mengakses area user', 'error')
            return redirect(url_for('admin_dashboard'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def require_admin(f):
    def decorated_function(*args, **kwargs):
        if 'admin' not in session:
            flash('Akses ditolak. Silakan login sebagai admin', 'error')
            return redirect(url_for('admin_login'))
        # Pastikan bukan user yang mencoba akses admin area
        if 'user_id' in session:
            flash('User tidak dapat mengakses area admin', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def require_guest_only(f):
    def decorated_function(*args, **kwargs):
        # Redirect jika sudah login sebagai user atau admin
        if 'user_id' in session:
            return redirect(url_for('dashboard'))
        if 'admin' in session:
            return redirect(url_for('admin_dashboard'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

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
        return render_template('index.html')

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
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
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
        venue_address = request.form['venue_address']
        
        couple_name = f"{bride_name} & {groom_name}"
        wedding_date = request.form.get('wedding_date', '')
        wedding_time = request.form.get('wedding_time', '')
        venue_name = request.form.get('venue_name', '')
        template_id = request.form.get('template_id', 1)
        custom_message = request.form.get('custom_message', '')
        guest_limit = int(request.form.get('guest_limit', 100))
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
            # Use default music
            background_music = request.form.get('default_background_music', '')
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
                    photo_path = os.path.join(app.config['PREWEDDING_FOLDER'], filename)
                    photo.save(photo_path)
                    prewedding_photos.append(filename)
        
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
        if not venue_address.strip():
            missing_fields.append('Alamat Venue')
            
        if missing_fields:
            flash(f'Field berikut wajib diisi: {", ".join(missing_fields)}', 'error')
            conn = get_db()
            wedding_templates = conn.execute('SELECT * FROM wedding_templates ORDER BY is_premium, name').fetchall()
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
                 bank_name, bank_account, account_holder, qris_code, guest_limit)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (session['user_id'], couple_name, bride_name, bride_title, bride_father, bride_mother, 
                  groom_name, groom_title, groom_father, groom_mother, wedding_date_final, wedding_time_final, venue_name, 
                  venue_address, template_id, custom_message, invitation_link, qr_code_base64, background_music,
                  json.dumps(prewedding_photos), bank_name, bank_account, account_holder, qris_code, guest_limit))
            
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
    wedding_templates = conn.execute('SELECT * FROM wedding_templates ORDER BY is_premium, name').fetchall()
    conn.close()
    
    return render_template('create_wedding_invitation.html', wedding_templates=wedding_templates)

@app.route('/wedding/<link>')
def view_wedding_invitation(link):
    conn = get_db()
    invitation = conn.execute(
        '''SELECT wi.*, wt.name as template_name, wt.color_scheme, wt.animations, wt.ornaments
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
    
    # Parse prewedding photos
    prewedding_photos = []
    if invitation_dict['prewedding_photos']:
        prewedding_photos = json.loads(invitation_dict['prewedding_photos'])
    
    return render_template('wedding_invitation_view.html', 
                         invitation=invitation_dict, guests=guests, prewedding_photos=prewedding_photos)

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

@app.route('/admin')
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
        template_id, 
        template['name'], 
        template['color_scheme']
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
            template['color_scheme']
        )
        
        if thumbnail_filename:
            conn.execute('UPDATE wedding_templates SET preview_image = ? WHERE id = ?', 
                        (thumbnail_filename, template['id']))
            success_count += 1
    
    conn.commit()
    conn.close()
    
    flash(f'Berhasil generate {success_count} dari {total_count} thumbnails!', 'success')
    return redirect(url_for('admin_wedding_templates'))

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
            
            # Handle file uploads
            template_file = ''
            preview_image = ''
            background_music = ''
            
            if 'template_file' in request.files:
                file = request.files['template_file']
                if file.filename != '':
                    filename = secure_filename(file.filename)
                    timestamp = str(int(datetime.now().timestamp()))
                    filename = f"{timestamp}_{filename}"
                    file_path = os.path.join(app.config['WEDDING_FOLDER'], filename)
                    file.save(file_path)
                    template_file = filename
            
            if 'preview_image' in request.files:
                file = request.files['preview_image']
                if file.filename != '':
                    filename = secure_filename(file.filename)
                    timestamp = str(int(datetime.now().timestamp()))
                    filename = f"{timestamp}_{filename}"
                    # Save to static/images/wedding_templates for web access
                    file_path = os.path.join('static/images/wedding_templates', filename)
                    file.save(file_path)
                    preview_image = filename
                    
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
                (name, description, category, template_file, preview_image, color_scheme, animations, background_music, ornaments, is_premium)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, description, category, template_file, preview_image, color_scheme, animations, background_music, ornaments, is_premium))
            conn.commit()
            conn.close()
            
            flash('Template wedding berhasil ditambahkan!', 'success')
            
        elif action == 'update_thumbnail':
            template_id = request.form['template_id']
            
            if 'preview_image' in request.files:
                file = request.files['preview_image']
                if file.filename != '':
                    filename = secure_filename(file.filename)
                    timestamp = str(int(datetime.now().timestamp()))
                    filename = f"{timestamp}_{filename}"
                    file_path = os.path.join('static/images/wedding_templates', filename)
                    file.save(file_path)
                    
                    conn = get_db()
                    conn.execute('UPDATE wedding_templates SET preview_image = ? WHERE id = ?', (filename, template_id))
                    conn.commit()
                    conn.close()
                    
                    flash('Thumbnail template berhasil diperbarui!', 'success')
        
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
        
        conn.close()
        
        debug_info = {
            'user_id': session.get('user_id', 'Not logged in'),
            'total_invitations': len(all_invitations),
            'user_invitations': len(current_user_invitations),
            'all_invitations': [dict(inv) for inv in all_invitations],
            'user_invitations_data': [dict(inv) for inv in current_user_invitations]
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

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
