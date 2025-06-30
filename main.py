from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import pyodbc
import os
from datetime import datetime, date, timedelta
from werkzeug.utils import secure_filename
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import webbrowser
import sys

app = Flask(__name__)
app.secret_key = 'devinova_pos_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Remove resource_path usage and use os.path.abspath for local paths
# Load Access DB config from config.json
with open('config.json', 'r') as f:
    CONFIG = json.load(f)

ACCESS_DB_PATH = os.path.abspath(CONFIG.get('access_db_path', 'devinova_pos.accdb'))

# Print the database path being used for absolute clarity
print("USING DATABASE FILE:", ACCESS_DB_PATH)

# Connection string for Access (requires Access ODBC driver)
def get_db_connection():
    conn_str = (
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        f'DBQ={ACCESS_DB_PATH};'
    )
    conn = pyodbc.connect(conn_str)
    return conn

def log_activity(user_id, username, action, details=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO activity_logs (user_id, username, action, details) VALUES (?, ?, ?, ?)",
        (user_id, username, action, details)
    )
    conn.commit()
    cursor.close()
    conn.close()

@app.route('/')
def index():
    if 'user_id' in session:
        if session['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('cashier_dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    try:
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        print(f"Login attempt: username={username}, password_hash={password}")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
                       (username, password))
        user = cursor.fetchone()
        print(f"Query result: {user}")
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]
            log_activity(user[0], user[1], 'login', 'User logged in')
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials!', 'error')
            return redirect(url_for('index'))
    except Exception as e:
        print(f"Login error: {e}")
        flash(f"Login error: {e}", 'error')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    if 'user_id' in session:
        log_activity(session['user_id'], session['username'], 'logout', 'User logged out')
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Access denied!', 'error')
        return redirect(url_for('index'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get low stock products
    cursor.execute('SELECT * FROM products WHERE stock < 10')
    low_stock = cursor.fetchall()

    # Get today's summary
    today = date.today()
    # Use new column names: sale_date and expense_date
    cursor.execute('''
        SELECT IIF(SUM(total_price) IS NULL, 0, SUM(total_price)) as total 
        FROM sales WHERE sale_date = ?
    ''', (today,))
    total_sales = cursor.fetchone()[0]

    cursor.execute('''
        SELECT IIF(SUM(amount_paid) IS NULL, 0, SUM(amount_paid)) as total 
        FROM services_sold WHERE sale_date = ?
    ''', (today,))
    total_services = cursor.fetchone()[0]

    cursor.execute('''
        SELECT IIF(SUM(amount) IS NULL, 0, SUM(amount)) as total 
        FROM expenses WHERE expense_date = ?
    ''', (today,))
    total_expenses = cursor.fetchone()[0]

    conn.close()

    return render_template('admin/dashboard.html', 
                         low_stock=low_stock,
                         total_sales=total_sales,
                         total_services=total_services,
                         total_expenses=total_expenses)

@app.route('/cashier')
def cashier_dashboard():
    if 'user_id' not in session:
        flash('Please login first!', 'error')
        return redirect(url_for('index'))

    return render_template('cashier/dashboard.html')

# Register blueprints
from routes.admin import admin_bp
from routes.cashier import cashier_bp
from routes.transcript import transcript_bp

app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(cashier_bp, url_prefix='/cashier')
app.register_blueprint(transcript_bp)

# Add admin routes directly to main app for navigation
@app.route('/admin/products')
def manage_products():
    return redirect(url_for('admin.manage_products'))

@app.route('/admin/services')
def manage_services():
    return redirect(url_for('admin.manage_services'))

@app.route('/admin/reports')
def view_reports():
    return redirect(url_for('admin.view_reports'))

@app.route('/admin/users')
def manage_users():
    return redirect(url_for('admin.manage_users'))

@app.route('/cashier/sale')
def process_sale():
    return redirect(url_for('cashier.process_sale'))

@app.route('/cashier/service')
def record_service():
    return redirect(url_for('cashier.record_service'))

@app.route('/cashier/expense')
def record_expense():
    return redirect(url_for('cashier.record_expense'))

@app.route('/cashier/report')
def daily_report():
    return redirect(url_for('cashier.daily_report'))

@app.route('/admin/stock-taking')
def stock_taking():
    return redirect(url_for('admin.stock_taking'))

@app.route('/cashier/stock-check')
def stock_check():
    return redirect(url_for('cashier.stock_check'))

# --- Enhanced Time Tracker for Multiple Computers ---
from flask import request
from datetime import timedelta

@app.route('/cashier/time-tracker')
def time_tracker():
    return render_template('cashier/time_tracker.html')

@app.route('/cashier/time-tracker/start', methods=['POST'])
def start_timer():
    computer = request.json.get('computer')
    if not computer:
        return {'success': False, 'message': 'No computer selected.'}
    key = f'timer_start_{computer}'
    session[key] = datetime.now().isoformat()
    return {'success': True, 'start_time': session[key]}

@app.route('/cashier/time-tracker/stop', methods=['POST'])
def stop_timer():
    computer = request.json.get('computer')
    if not computer:
        return {'success': False, 'message': 'No computer selected.'}
    key = f'timer_start_{computer}'
    start_time = session.get(key)
    if not start_time:
        return {'success': False, 'message': 'Timer not started.'}
    start_dt = datetime.fromisoformat(start_time)
    end_dt = datetime.now()
    duration = int((end_dt - start_dt).total_seconds() // 60)  # minutes
    # Pricing: 1 shilling per minute, but 50 per hour (60 min) with 10 sh discount
    if duration >= 60:
        hours = duration // 60
        mins = duration % 60
        amount = hours * 50 + mins * 1
    else:
        amount = duration * 1
    session.pop(key, None)
    return {'success': True, 'duration': duration, 'amount': amount}

@app.route('/cashier/time-tracker/status')
def time_tracker_status():
    # Return all timer start times for computers 1-4
    status = {}
    for i in range(1, 5):
        key = f'timer_start_{i}'
        status[key] = session.get(key)
    return status

# Store reverse timer state in session for persistence
@app.route('/cashier/time-tracker/set_reverse', methods=['POST'])
def set_reverse_timer():
    data = request.get_json()
    computer = str(data.get('computer'))
    amount = int(data.get('amount', 0))
    if not computer or amount < 1:
        return {'success': False, 'message': 'Invalid input.'}
    session[f'reverse_time_{computer}'] = amount * 60  # seconds
    session[f'reverse_start_{computer}'] = datetime.now().isoformat()
    return {'success': True}

@app.route('/cashier/time-tracker/reverse_status')
def reverse_timer_status():
    # Return all reverse timer states for computers 1-4
    status = {}
    for i in range(1, 5):
        status[f'reverse_time_{i}'] = session.get(f'reverse_time_{i}')
        status[f'reverse_start_{i}'] = session.get(f'reverse_start_{i}')
    return status

# In-memory chat storage (replace with DB in production)
CHAT_MESSAGES = []

# Helper to clean up old messages (older than 24 hours)
def cleanup_chat_messages():
    now = datetime.now()
    cutoff = now - timedelta(hours=24)
    global CHAT_MESSAGES
    CHAT_MESSAGES = [msg for msg in CHAT_MESSAGES if isinstance(msg['timestamp'], datetime) and msg['timestamp'] > cutoff]

@app.route('/chatbox')
def chatbox():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('chatbox.html')

@app.route('/chat/messages')
def chat_messages():
    if 'user_id' not in session:
        return jsonify({'messages': []})
    cleanup_chat_messages()
    # Return messages as strings for JSON
    return jsonify({'messages': [
        {
            'sender': m['sender'],
            'text': m['text'],
            'timestamp': m['timestamp'].strftime('%Y-%m-%d %H:%M') if isinstance(m['timestamp'], datetime) else str(m['timestamp'])
        } for m in CHAT_MESSAGES[-100:]
    ]})

@app.route('/chat/send', methods=['POST'])
def chat_send():
    if 'user_id' not in session:
        return '', 401
    data = request.get_json()
    text = data.get('text', '').strip()
    if not text:
        return '', 400
    sender = session.get('role', 'User').capitalize()
    now = datetime.now()
    CHAT_MESSAGES.append({'sender': sender, 'text': text, 'timestamp': now})
    cleanup_chat_messages()
    return '', 204

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Create tables with Access-compatible SQL
    try:
        cursor.execute('''CREATE TABLE users (
            id COUNTER PRIMARY KEY,
            username TEXT(255) UNIQUE,
            password TEXT(255),
            role TEXT(50),
            created_at DATETIME
        )''')
    except Exception as e:
        pass  # Table may already exist
    try:
        cursor.execute('''CREATE TABLE products (
            id COUNTER PRIMARY KEY,
            name TEXT(255),
            description MEMO,
            price DOUBLE,
            stock INT,
            image_path TEXT(255),
            category TEXT(100),
            created_at DATETIME
        )''')
    except Exception as e:
        pass
    try:
        cursor.execute('''CREATE TABLE services (
            id COUNTER PRIMARY KEY,
            name TEXT(255),
            default_price DOUBLE,
            created_at DATETIME
        )''')
    except Exception as e:
        pass
    try:
        cursor.execute('''CREATE TABLE sales (
            id COUNTER PRIMARY KEY,
            product_id INT,
            quantity INT,
            unit_price DOUBLE,
            total_price DOUBLE,
            payment_method TEXT(50),
            cashier_id INT,
            date DATETIME,
            created_at DATETIME
        )''')
    except Exception as e:
        pass
    try:
        cursor.execute('''CREATE TABLE services_sold (
            id COUNTER PRIMARY KEY,
            service_id INT,
            amount_paid DOUBLE,
            date DATETIME,
            cashier_id INT,
            created_at DATETIME
        )''')
    except Exception as e:
        pass
    try:
        cursor.execute('''CREATE TABLE expenses (
            id COUNTER PRIMARY KEY,
            name TEXT(255),
            amount DOUBLE,
            notes MEMO,
            provider TEXT(255),
            money_source TEXT(100),
            date DATETIME,
            cashier_id INT,
            created_at DATETIME
        )''')
    except Exception as e:
        pass
    try:
        cursor.execute('''CREATE TABLE activity_logs (
            id COUNTER PRIMARY KEY,
            user_id INT,
            username TEXT(255),
            action TEXT(255),
            details MEMO,
            log_time DATETIME
        )''')
    except Exception as e:
        pass
    try:
        cursor.execute('''CREATE TABLE students (
            id AUTOINCREMENT PRIMARY KEY,
            admission_no TEXT(20),
            name TEXT(255),
            email TEXT(255),
            phone TEXT(50),
            amount_paid DOUBLE,
            admission_date DATE,
            ms_word DOUBLE,
            ms_excel DOUBLE,
            ms_access DOUBLE,
            ms_publisher DOUBLE,
            ms_powerpoint DOUBLE,
            internet_email DOUBLE,
            created_at DATETIME
        )''')
    except Exception as e:
        pass
    try:
        cursor.execute('''CREATE TABLE student_payments (
            id AUTOINCREMENT PRIMARY KEY,
            student_id INT,
            admission_no TEXT(20),
            amount DOUBLE,
            payment_date DATETIME,
            notes MEMO,
            cashier_id INT,
            created_at DATETIME
        )''')
    except Exception as e:
        pass
    try:
        cursor.execute('''CREATE TABLE transcript_requests (
            id AUTOINCREMENT PRIMARY KEY,
            admission_no TEXT(20),
            student_name TEXT(255),
            request_date DATETIME,
            status TEXT(50),
            message MEMO
        )''')
    except Exception as e:
        pass
    try:
        cursor.execute('''CREATE TABLE transcript_receipts (
            id AUTOINCREMENT PRIMARY KEY,
            request_id INT,
            admission_no TEXT(20),
            student_name TEXT(255),
            receipt_path TEXT(255),
            generated_at DATETIME
        )''')
    except Exception as e:
        pass
    try:
        cursor.execute('''CREATE TABLE student_certificates (
            id AUTOINCREMENT PRIMARY KEY,
            admission_no TEXT(20),
            file_path TEXT(255),
            uploaded_at DATETIME
        )''')
    except Exception as e:
        pass
    # Ensure payment_method and mpesa_code columns exist in student_payments
    try:
        cursor.execute("SELECT payment_method, mpesa_code FROM student_payments WHERE 1=0")
    except Exception:
        try:
            cursor.execute("ALTER TABLE student_payments ADD COLUMN payment_method TEXT(50)")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE student_payments ADD COLUMN mpesa_code TEXT(50)")
        except Exception:
            pass
    # Create default admin user
    try:
        cursor.execute('SELECT COUNT(*) FROM users WHERE role = ?', ("admin",))
        if cursor.fetchone()[0] == 0:
            admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
            cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', 
                          ('admin', admin_password, 'admin'))
    except Exception as e:
        pass
    # Create default cashier user
    try:
        cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', ("cashier",))
        if cursor.fetchone()[0] == 0:
            cashier_password = hashlib.sha256('cashier123'.encode()).hexdigest()
            cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', 
                          ('cashier', cashier_password, 'cashier'))
    except Exception as e:
        pass
    conn.commit()
    cursor.close()
    conn.close()

def send_email_alert(subject, body, to_email='devinovacyber@gmail.com'):
    # Gmail SMTP setup
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = 'devinovacyber@gmail.com'  # Use your Gmail address
    sender_password = 'YOUR_APP_PASSWORD'  # Use an app password, not your Gmail password

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")

# Diagnostic block to test Access connection and query database
if __name__ == "__main__":
    # Load config
    with open('config.json', 'r') as f:
        config = json.load(f)
    db_path = os.path.abspath(config.get('access_db_path', 'devinova_pos.accdb'))
    conn_str = (
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        f'DBQ={db_path};'
    )
    print(f"Testing connection to: {db_path}")
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        # List all tables
        tables = [row.table_name for row in cursor.tables(tableType='TABLE')]
        print("Tables in database:", tables)
        # Try a simple query on products
        if 'products' in [t.lower() for t in tables]:
            try:
                cursor.execute('SELECT * FROM [products]')
                rows = cursor.fetchall()
                print(f"First row in products: {rows[0] if rows else 'No rows found'}")
            except Exception as e:
                print(f"Error querying products table: {e}")
        else:
            print("'products' table not found in database.")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database connection or query failed: {e}")

if __name__ == '__main__':
    # Initialize the database and tables if they do not exist
    try:
        init_db()
        print('Database initialized successfully.')
    except Exception as e:
        print(f'Error initializing database: {e}')
    # Open the app in the default web browser automatically
    webbrowser.open('http://127.0.0.1:5000')
    app.run(host='127.0.0.1', port=5000, debug=True)  # Enable debug mode for error details

def find_wkhtmltopdf_executable():
    """
    Try to find wkhtmltopdf in the default location, environment variable, or system PATH.
    Returns the path if found, else None.
    """
    import shutil
    # 1. Check environment variable
    env_path = os.environ.get('WKHTMLTOPDF_PATH')
    if env_path and os.path.isfile(env_path):
        return env_path
    # 2. Check default install location (Windows)
    default_path = r'C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'
    if os.path.isfile(default_path):
        return default_path
    # 3. Check system PATH
    exe_path = shutil.which('wkhtmltopdf')
    if exe_path:
        return exe_path
    return None