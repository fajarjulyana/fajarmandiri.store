
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, jsonify
import sqlite3
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create uploads directory if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def init_db():
    conn = sqlite3.connect('fajar_mandiri.db')
    c = conn.cursor()
    
    # Create orders table
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama TEXT NOT NULL,
        email TEXT NOT NULL,
        whatsapp TEXT NOT NULL,
        jenis_cetakan TEXT NOT NULL,
        jumlah INTEGER NOT NULL,
        catatan TEXT,
        file_path TEXT,
        status TEXT NOT NULL DEFAULT 'Pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Create admin table
    c.execute('''CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    )''')
    
    # Insert default admin if not exists
    c.execute('SELECT COUNT(*) FROM admin WHERE username = ?', ('fajar',))
    if c.fetchone()[0] == 0:
        hashed_password = generate_password_hash('fajar')
        c.execute('INSERT INTO admin (username, password) VALUES (?, ?)', ('fajar', hashed_password))
    
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect('fajar_mandiri.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/order', methods=['GET', 'POST'])
def order():
    if request.method == 'POST':
        nama = request.form['nama']
        email = request.form['email']
        whatsapp = request.form['whatsapp']
        jenis_cetakan = request.form['jenis_cetakan']
        jumlah = request.form['jumlah']
        catatan = request.form['catatan']
        
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
        conn.execute('''INSERT INTO orders (nama, email, whatsapp, jenis_cetakan, jumlah, catatan, file_path, status)
                       VALUES (?, ?, ?, ?, ?, ?, ?, 'Pending')''',
                    (nama, email, whatsapp, jenis_cetakan, jumlah, catatan, file_path))
        conn.commit()
        conn.close()
        
        return redirect(url_for('status'))
    
    return render_template('order.html')

@app.route('/status')
def status():
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    
    conn = get_db()
    query = 'SELECT * FROM orders WHERE 1=1'
    params = []
    
    if search:
        query += ' AND (nama LIKE ? OR email LIKE ? OR whatsapp LIKE ? OR id = ?)'
        search_param = f'%{search}%'
        params.extend([search_param, search_param, search_param, search])
    
    if status_filter:
        query += ' AND status = ?'
        params.append(status_filter)
    
    query += ' ORDER BY id DESC'
    
    orders = conn.execute(query, params).fetchall()
    conn.close()
    
    return render_template('status.html', orders=orders, search=search, status_filter=status_filter)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/cv_generator')
def cv_generator():
    return render_template('cv_generator.html')

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
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

@app.route('/admin')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST' and 'update_status' in request.form:
        order_id = request.form['order_id']
        status = request.form['status']
        
        conn = get_db()
        conn.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
        conn.commit()
        conn.close()
        
        return redirect(url_for('admin_dashboard'))
    
    conn = get_db()
    orders = conn.execute('SELECT * FROM orders ORDER BY id DESC').fetchall()
    conn.close()
    
    return render_template('admin/index.html', orders=orders)

@app.route('/admin/view_order/<int:order_id>')
def view_order(order_id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    conn = get_db()
    order = conn.execute('SELECT * FROM orders WHERE id = ?', (order_id,)).fetchone()
    conn.close()
    
    if not order:
        flash('Order not found')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/view_order.html', order=order)

@app.route('/admin/update_status', methods=['POST'])
def update_status():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    order_id = request.form['order_id']
    status = request.form['status']
    
    conn = get_db()
    conn.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/download/<int:order_id>')
def download_file(order_id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    conn = get_db()
    order = conn.execute('SELECT file_path FROM orders WHERE id = ?', (order_id,)).fetchone()
    conn.close()
    
    if order and order['file_path'] and os.path.exists(order['file_path']):
        return send_file(order['file_path'], as_attachment=True)
    
    flash('File not found')
    return redirect(url_for('admin_dashboard'))

@app.route('/payment_webhook', methods=['POST'])
def payment_webhook():
    if request.method != 'POST':
        return jsonify({"status": "error", "message": "Method Not Allowed"}), 405
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Invalid JSON"}), 400
        
        # Log webhook for debugging
        log_data = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {json.dumps(data)}\n"
        with open('webhook_log.txt', 'a') as f:
            f.write(log_data)
        
        return jsonify({"status": "success", "message": "Webhook received"}), 200
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5004, debug=True)
