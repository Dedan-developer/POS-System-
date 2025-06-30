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

# Create missing tables with correct columns for your app
create_tables_sql = [
    '''CREATE TABLE sales (
        id COUNTER PRIMARY KEY,
        product_id INTEGER,
        quantity INTEGER,
        unit_price DOUBLE,
        total_price DOUBLE,
        payment_method TEXT(50),
        cashier_id INTEGER,
        [date] DATETIME,
        created_at DATETIME
    )''',
    '''CREATE TABLE services_sold (
        id COUNTER PRIMARY KEY,
        service_id INTEGER,
        amount_paid DOUBLE,
        [date] DATETIME,
        cashier_id INTEGER,
        created_at DATETIME
    )''',
    '''CREATE TABLE expenses (
        id COUNTER PRIMARY KEY,
        name TEXT(255),
        amount DOUBLE,
        notes MEMO,
        provider TEXT(255),
        money_source TEXT(100),
        [date] DATETIME,
        cashier_id INTEGER,
        created_at DATETIME
    )'''
]

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    for sql in create_tables_sql:
        try:
            cursor.execute(sql)
            print('Table created.')
        except Exception as e:
            print('Table may already exist or error:', e)
    conn.commit()
    cursor.close()
    conn.close()
    print('All tables processed.')
except Exception as e:
    print('Database connection error:', e)
