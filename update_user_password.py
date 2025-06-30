import pyodbc
import json
import os
import hashlib

# --- CONFIG ---
USERNAME = 'admin'  # Change this to the username you want to update
NEW_PASSWORD = 'newpassword123'  # Change this to your new password

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)
db_path = config.get('access_db_path', 'devinova_pos.accdb')
db_path = os.path.abspath(db_path)

conn_str = (
    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
    f'DBQ={db_path};'
)

hashed_password = hashlib.sha256(NEW_PASSWORD.encode()).hexdigest()

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET password = ? WHERE username = ?', (hashed_password, USERNAME))
    conn.commit()
    print(f"Password for user '{USERNAME}' updated to SHA256 hash of '{NEW_PASSWORD}'.")
    cursor.close()
    conn.close()
except Exception as e:
    print('Error updating password:', e)
