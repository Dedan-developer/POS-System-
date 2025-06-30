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

# Drop and recreate all relevant tables with correct columns
# WARNING: This will delete all data in these tables!
table_sql = [
    'DROP TABLE sales',
    'DROP TABLE services_sold',
    'DROP TABLE expenses',
    '''CREATE TABLE sales (
        id COUNTER PRIMARY KEY,
        product_id INTEGER,
        quantity INTEGER,
        unit_price DOUBLE,
        total_price DOUBLE,
        payment_method TEXT(50),
        cashier_id INTEGER,
        sale_date DATETIME,
        created_at DATETIME
    )''',
    '''CREATE TABLE services_sold (
        id COUNTER PRIMARY KEY,
        service_id INTEGER,
        amount_paid DOUBLE,
        sale_date DATETIME,
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
        expense_date DATETIME,
        cashier_id INTEGER,
        created_at DATETIME
    )'''
]

def try_execute(cursor, sql):
    try:
        cursor.execute(sql)
        print('Executed:', sql.split('(')[0].strip())
    except Exception as e:
        print('Error or already exists:', e)

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    # Drop tables if they exist
    for sql in table_sql[:3]:
        try_execute(cursor, sql)
    # Create tables
    for sql in table_sql[3:]:
        try_execute(cursor, sql)
    conn.commit()
    cursor.close()
    conn.close()
    print('Tables updated to preferences.')
except Exception as e:
    print('Database connection error:', e)
