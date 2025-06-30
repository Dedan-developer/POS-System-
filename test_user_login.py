import pyodbc
import json
import os
import hashlib

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)
db_path = os.path.abspath(config.get('access_db_path', 'devinova_pos.accdb'))
conn_str = (
    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
    f'DBQ={db_path};'
)

username = 'admin'
password = hashlib.sha256('admin123'.encode()).hexdigest()
print('Checking:', username, password)

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    print('Query result:', user)
    cursor.close()
    conn.close()
except Exception as e:
    print('Database error:', e)
