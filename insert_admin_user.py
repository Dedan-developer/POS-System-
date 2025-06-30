import pyodbc
import json
import os
import datetime

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)
db_path = config.get('access_db_path', 'devinova_pos.accdb')
db_path = os.path.abspath(db_path)

conn_str = (
    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
    f'DBQ={db_path};'
)

admin_username = 'admin'
admin_password = '0192023a7bbd73250516f069df18b500'  # SHA256 for 'admin123'
admin_role = 'admin'
created_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    # Check if admin already exists
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (admin_username,))
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO users (username, password, role, created_at) VALUES (?, ?, ?, ?)",
            (admin_username, admin_password, admin_role, created_at)
        )
        conn.commit()
        print('Admin user inserted.')
    else:
        print('Admin user already exists.')
    cursor.close()
    conn.close()
except Exception as e:
    print('Error inserting admin user:', e)
