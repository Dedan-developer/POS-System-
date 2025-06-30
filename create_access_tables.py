import pyodbc
import json
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

table_sql = [
    '''CREATE TABLE users (
        id COUNTER PRIMARY KEY,
        username TEXT(255),
        password TEXT(255),
        role TEXT(50),
        created_at DATETIME
    )''',
    '''CREATE TABLE products (
        id COUNTER PRIMARY KEY,
        name TEXT(255),
        description MEMO,
        price DOUBLE,
        stock INTEGER,
        image_path TEXT(255),
        category TEXT(100),
        created_at DATETIME
    )''',
    '''CREATE TABLE services (
        id COUNTER PRIMARY KEY,
        name TEXT(255),
        default_price DOUBLE,
        created_at DATETIME
    )''',
    '''CREATE TABLE sales (
        id COUNTER PRIMARY KEY,
        product_id INTEGER,
        quantity INTEGER,
        unit_price DOUBLE,
        total_price DOUBLE,
        payment_method TEXT(50),
        cashier_id INTEGER,
        date DATETIME,
        created_at DATETIME
    )''',
    '''CREATE TABLE services_sold (
        id COUNTER PRIMARY KEY,
        service_id INTEGER,
        amount_paid DOUBLE,
        date DATETIME,
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
        date DATETIME,
        cashier_id INTEGER,
        created_at DATETIME
    )''',
    '''CREATE TABLE activity_logs (
        id COUNTER PRIMARY KEY,
        user_id INTEGER,
        username TEXT(255),
        action TEXT(255),
        details MEMO,
        log_time DATETIME
    )'''
]

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    for sql in table_sql:
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
