
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

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['TEMPLATES_FOLDER'] = 'cv_templates'
app.config['WEDDING_FOLDER'] = 'wedding_invitations'

# Create necessary directories
for folder in [app.config['UPLOAD_FOLDER'], app.config['TEMPLATES_FOLDER'], app.config['WEDDING_FOLDER']]:
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

def init_db():
    conn = sqlite3.connect('fajar_mandiri.db')
    c = conn.cursor()
    
    # Users table for both Google OAuth and manual registration
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        google_id TEXT,
        email TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        password TEXT,
        picture TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Orders table
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        nama TEXT NOT NULL,
        email TEXT NOT NULL,
        whatsapp TEXT NOT NULL,
        jenis_cetakan TEXT NOT NULL,
        jumlah INTEGER NOT NULL,
        catatan TEXT,
        file_path TEXT,
        status TEXT NOT NULL DEFAULT 'Pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    # CV templates table
    c.execute('''CREATE TABLE IF NOT EXISTS cv_templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        template_file TEXT NOT NULL,
        preview_image TEXT,
        is_premium BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Wedding invitations table
    c.execute('''CREATE TABLE IF NOT EXISTS wedding_invitations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        couple_name TEXT NOT NULL,
        bride_name TEXT NOT NULL,
        groom_name TEXT NOT NULL,
        wedding_date DATE NOT NULL,
        venue_name TEXT NOT NULL,
        venue_address TEXT NOT NULL,
        template_id INTEGER NOT NULL,
        custom_message TEXT,
        invitation_link TEXT UNIQUE NOT NULL,
        qr_code TEXT,
        guest_limit INTEGER DEFAULT 100,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
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
    
    # Insert default CV templates
    default_templates = [
        ('Modern Professional', 'Clean and modern design perfect for corporate jobs', 'modern_pro.html', 'modern_pro_preview.jpg', 0),
        ('Creative Designer', 'Colorful and creative template for designers', 'creative.html', 'creative_preview.jpg', 0),
        ('Minimalist', 'Simple and elegant minimalist design', 'minimalist.html', 'minimalist_preview.jpg', 0),
        ('Executive', 'Professional template for senior positions', 'executive.html', 'executive_preview.jpg', 1),
        ('Tech Specialist', 'Perfect for IT and tech professionals', 'tech.html', 'tech_preview.jpg', 0),
        ('Academic', 'Ideal for researchers and academics', 'academic.html', 'academic_preview.jpg', 0),
        ('Sales & Marketing', 'Dynamic template for sales professionals', 'sales.html', 'sales_preview.jpg', 1),
        ('Healthcare', 'Professional template for medical professionals', 'healthcare.html', 'healthcare_preview.jpg', 1),
        ('Startup', 'Modern template for startup enthusiasts', 'startup.html', 'startup_preview.jpg', 0),
        ('International', 'Global standard professional template', 'international.html', 'international_preview.jpg', 1)
    ]
    
    for template in default_templates:
        c.execute('INSERT OR IGNORE INTO cv_templates (name, description, template_file, preview_image, is_premium) VALUES (?, ?, ?, ?, ?)', template)
    
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect('fajar_mandiri.db')
    conn.row_factory = sqlite3.Row
    return conn

def require_auth(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def require_admin(f):
    def decorated_function(*args, **kwargs):
        if 'admin' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Manual Authentication routes
@app.route('/login', methods=['GET', 'POST'])
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
            
            flash(f'Selamat datang, {user["name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Email atau password salah!', 'error')
    
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validasi
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
        
        # Hash password dan simpan user
        hashed_password = generate_password_hash(password)
        cursor = conn.execute('''
            INSERT INTO users (name, email, password, google_id) 
            VALUES (?, ?, ?, ?)
        ''', (name, email, hashed_password, ''))
        user_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        # Auto login setelah registrasi
        session['user_id'] = user_id
        session['user_name'] = name
        session['user_email'] = email
        session['user_picture'] = ''
        
        flash(f'Registrasi berhasil! Selamat datang, {name}!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('auth/register.html')

# Google OAuth routes (keep existing)
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
        flash('Google OAuth tidak dikonfigurasi. Silakan hubungi administrator.', 'error')
        return redirect(url_for('index'))

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
    
    # Get user info from Google
    service = build('oauth2', 'v2', credentials=credentials)
    user_info = service.userinfo().get().execute()
    
    # Save or update user in database
    conn = get_db()
    existing_user = conn.execute('SELECT * FROM users WHERE google_id = ?', (user_info['id'],)).fetchone()
    
    if existing_user:
        user_id = existing_user['id']
    else:
        cursor = conn.execute(
            'INSERT INTO users (google_id, email, name, picture) VALUES (?, ?, ?, ?)',
            (user_info['id'], user_info['email'], user_info['name'], user_info.get('picture', ''))
        )
        user_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    session['user_id'] = user_id
    session['user_name'] = user_info['name']
    session['user_email'] = user_info['email']
    session['user_picture'] = user_info.get('picture', '')
    
    flash(f'Selamat datang, {user_info["name"]}!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/signout')
def signout():
    session.clear()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('index'))

# Main routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
@require_auth
def dashboard():
    conn = get_db()
    
    # Get user's recent orders
    orders = conn.execute(
        'SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC LIMIT 5',
        (session['user_id'],)
    ).fetchall()
    
    # Get user's wedding invitations
    invitations = conn.execute(
        'SELECT * FROM wedding_invitations WHERE user_id = ? ORDER BY created_at DESC LIMIT 3',
        (session['user_id'],)
    ).fetchall()
    
    conn.close()
    
    return render_template('dashboard.html', orders=orders, invitations=invitations)

# Order routes
@app.route('/order', methods=['GET', 'POST'])
@require_auth
def order():
    if request.method == 'POST':
        nama = request.form['nama']
        email = request.form['email']
        whatsapp = request.form['whatsapp']
        jenis_cetakan = request.form['jenis_cetakan']
        jumlah = int(request.form['jumlah'])
        catatan = request.form.get('catatan', '')
        
        file_path = ''
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                filename = secure_filename(file.filename)
                timestamp = str(int(datetime.now().timestamp()))
                filename = f"{timestamp}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
        
        conn = get_db()
        conn.execute('''
            INSERT INTO orders (user_id, nama, email, whatsapp, jenis_cetakan, jumlah, catatan, file_path, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Pending')
        ''', (session['user_id'], nama, email, whatsapp, jenis_cetakan, jumlah, catatan, file_path))
        conn.commit()
        conn.close()
        
        flash('Pesanan berhasil dibuat!', 'success')
        return redirect(url_for('my_orders'))
    
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
    
    # Get template
    conn = get_db()
    template = conn.execute('SELECT * FROM cv_templates WHERE id = ?', (template_id,)).fetchone()
    conn.close()
    
    if not template:
        flash('Template tidak ditemukan!', 'error')
        return redirect(url_for('cv_generator'))
    
    # Collect form data
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
    
    # Process education
    if request.form.getlist('pendidikan_institusi'):
        for i in range(len(request.form.getlist('pendidikan_institusi'))):
            if request.form.getlist('pendidikan_institusi')[i]:
                cv_data['pendidikan'].append({
                    'institusi': request.form.getlist('pendidikan_institusi')[i],
                    'jurusan': request.form.getlist('pendidikan_jurusan')[i] if i < len(request.form.getlist('pendidikan_jurusan')) else '',
                    'tahun': request.form.getlist('pendidikan_tahun')[i] if i < len(request.form.getlist('pendidikan_tahun')) else ''
                })
    
    # Process experience
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
            # Convert to base64
            foto_data = foto.read()
            foto_base64 = base64.b64encode(foto_data).decode()
    
    cv_data['foto'] = foto_base64
    
    # Generate PDF (simplified for now - you can integrate with a PDF library)
    # For now, return the CV data as JSON for testing
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
    conn.close()
    
    return render_template('wedding_invitations.html', invitations=invitations)

@app.route('/create-wedding-invitation', methods=['GET', 'POST'])
@require_auth
def create_wedding_invitation():
    if request.method == 'POST':
        bride_name = request.form['bride_name']
        groom_name = request.form['groom_name']
        couple_name = f"{bride_name} & {groom_name}"
        wedding_date = request.form['wedding_date']
        venue_name = request.form['venue_name']
        venue_address = request.form['venue_address']
        template_id = request.form['template_id']
        custom_message = request.form.get('custom_message', '')
        guest_limit = int(request.form.get('guest_limit', 100))
        
        # Generate unique invitation link
        invitation_code = str(uuid.uuid4())[:8]
        invitation_link = f"{bride_name.lower()}-{groom_name.lower()}-{invitation_code}"
        
        # Generate QR Code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url_for('view_wedding_invitation', link=invitation_link, _external=True))
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        conn = get_db()
        conn.execute('''
            INSERT INTO wedding_invitations 
            (user_id, couple_name, bride_name, groom_name, wedding_date, venue_name, venue_address, 
             template_id, custom_message, invitation_link, qr_code, guest_limit)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session['user_id'], couple_name, bride_name, groom_name, wedding_date, venue_name, 
              venue_address, template_id, custom_message, invitation_link, qr_code_base64, guest_limit))
        conn.commit()
        conn.close()
        
        flash('Undangan pernikahan berhasil dibuat!', 'success')
        return redirect(url_for('wedding_invitations'))
    
    # Wedding templates (you can expand this)
    wedding_templates = [
        {'id': 1, 'name': 'Classic Elegant', 'preview': 'classic_preview.jpg'},
        {'id': 2, 'name': 'Modern Minimalist', 'preview': 'modern_preview.jpg'},
        {'id': 3, 'name': 'Floral Garden', 'preview': 'floral_preview.jpg'},
        {'id': 4, 'name': 'Vintage Romance', 'preview': 'vintage_preview.jpg'},
        {'id': 5, 'name': 'Beach Wedding', 'preview': 'beach_preview.jpg'},
        {'id': 6, 'name': 'Royal Gold', 'preview': 'royal_preview.jpg'},
        {'id': 7, 'name': 'Rustic Charm', 'preview': 'rustic_preview.jpg'},
        {'id': 8, 'name': 'Art Deco', 'preview': 'artdeco_preview.jpg'},
        {'id': 9, 'name': 'Botanical', 'preview': 'botanical_preview.jpg'},
        {'id': 10, 'name': 'Luxury Marble', 'preview': 'marble_preview.jpg'}
    ]
    
    return render_template('create_wedding_invitation.html', wedding_templates=wedding_templates)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/wedding/<link>')
def view_wedding_invitation(link):
    conn = get_db()
    invitation = conn.execute(
        'SELECT * FROM wedding_invitations WHERE invitation_link = ? AND is_active = 1',
        (link,)
    ).fetchone()
    
    if not invitation:
        return render_template('404.html'), 404
    
    # Get RSVP responses
    guests = conn.execute(
        'SELECT * FROM wedding_guests WHERE invitation_id = ?',
        (invitation['id'],)
    ).fetchall()
    
    conn.close()
    
    return render_template('wedding_invitation_view.html', invitation=invitation, guests=guests)

@app.route('/rsvp/<int:invitation_id>', methods=['POST'])
def rsvp_wedding(invitation_id):
    name = request.form['name']
    phone = request.form.get('phone', '')
    email = request.form.get('email', '')
    attendance = request.form['attendance']
    guest_count = int(request.form.get('guest_count', 1))
    message = request.form.get('message', '')
    
    conn = get_db()
    conn.execute('''
        INSERT INTO wedding_guests (invitation_id, name, phone, email, attendance, guest_count, message)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (invitation_id, name, phone, email, attendance, guest_count, message))
    conn.commit()
    conn.close()
    
    flash('Terima kasih atas konfirmasi kehadiran Anda!', 'success')
    return redirect(request.referrer)

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
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
    
    # Get statistics
    total_users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    total_orders = conn.execute('SELECT COUNT(*) FROM orders').fetchone()[0]
    pending_orders = conn.execute('SELECT COUNT(*) FROM orders WHERE status = "Pending"').fetchone()[0]
    total_invitations = conn.execute('SELECT COUNT(*) FROM wedding_invitations').fetchone()[0]
    
    # Get recent orders
    recent_orders = conn.execute('''
        SELECT o.*, u.name as user_name 
        FROM orders o 
        LEFT JOIN users u ON o.user_id = u.id 
        ORDER BY o.created_at DESC 
        LIMIT 10
    ''').fetchall()
    
    conn.close()
    
    stats = {
        'total_users': total_users,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_invitations': total_invitations
    }
    
    return render_template('admin/dashboard.html', stats=stats, recent_orders=recent_orders)

@app.route('/admin/orders')
@require_admin
def admin_orders():
    conn = get_db()
    orders = conn.execute('''
        SELECT o.*, u.name as user_name, u.email as user_email
        FROM orders o 
        LEFT JOIN users u ON o.user_id = u.id 
        ORDER BY o.created_at DESC
    ''').fetchall()
    conn.close()
    
    return render_template('admin/orders.html', orders=orders)

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

@app.route('/admin/update-order-status', methods=['POST'])
@require_admin
def update_order_status():
    order_id = request.form['order_id']
    status = request.form['status']
    
    conn = get_db()
    conn.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
    conn.commit()
    conn.close()
    
    flash('Status pesanan berhasil diupdate!', 'success')
    return redirect(url_for('admin_orders'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
