import pyodbc
import json
import os

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)
db_path = os.path.abspath(config.get('access_db_path', 'devinova_pos.accdb'))
conn_str = (
    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
    f'DBQ={db_path};'
)

def print_table_columns(table_name):
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM {table_name}')
        print(f'{table_name} columns:', [column[0] for column in cursor.description])
        cursor.close()
        conn.close()
    except Exception as e:
        print(f'Error reading {table_name} table:', e)

for table in ['sales', 'services_sold', 'expenses', 'sales_extended']:
    print_table_columns(table)
