import pyodbc
import json
import sys
import os

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)
db_path = config.get('access_db_path', 'devinova_pos.accdb')
db_path = os.path.abspath(db_path)

conn_str = (
    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
    f'DBQ={db_path};'
)

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    print("Connected to database:", db_path)
    # List all tables
    for row in cursor.tables(tableType='TABLE'):
        print("Table:", row.table_name)
    cursor.close()
    conn.close()
except Exception as e:
    print("Database connection error:", e)
    sys.exit(1)