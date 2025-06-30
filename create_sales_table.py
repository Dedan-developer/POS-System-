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

sales_table_sql = '''
CREATE TABLE sales (
    id COUNTER PRIMARY KEY,
    product_id INTEGER,
    quantity INTEGER,
    unit_price DOUBLE,
    total_price DOUBLE,
    payment_method TEXT(50),
    cashier_id INTEGER,
    date DATETIME,
    created_at DATETIME
)'''

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    try:
        cursor.execute(sales_table_sql)
        print('sales table created.')
    except Exception as e:
        print('sales table may already exist or error:', e)
    conn.commit()
    cursor.close()
    conn.close()
    print('Done.')
except Exception as e:
    print('Database connection error:', e)
