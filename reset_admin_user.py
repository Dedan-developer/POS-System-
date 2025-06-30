import pyodbc
import json
import os
import datetime

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)
db_path = os.path.abspath(config.get('access_db_path', 'devinova_pos.accdb'))
conn_str = (
    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
    f'DBQ={db_path};'
)

admin_username = 'admin'
# Correct SHA256 hash for 'admin123'
admin_password = '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9'
admin_role = 'admin'
created_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    # Delete all users
    cursor.execute('DELETE FROM users')
    # Insert only the correct admin user
    cursor.execute(
        "INSERT INTO users (username, password, role, created_at) VALUES (?, ?, ?, ?)",
        (admin_username, admin_password, admin_role, created_at)
    )
    conn.commit()
    print('All users deleted. Admin user inserted.')
    cursor.close()
    conn.close()
except Exception as e:
    print('Error resetting users table:', e)
