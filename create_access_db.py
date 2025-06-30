import os
import pyodbc

db_path = "devinova_pos.accdb"

# Create the Access database file if it doesn't exist
if not os.path.exists(db_path):
    import pypyodbc
    pypyodbc.win_create_mdb(db_path)
    print(f"Database {db_path} created.")
else:
    print(f"Database {db_path} already exists.")

# Connect to the database
conn_str = (
    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
    f'DBQ={db_path};'
)
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Create the activity_logs table
cursor.execute("""
CREATE TABLE activity_logs (
    id AUTOINCREMENT PRIMARY KEY,
    user_id INTEGER,
    username TEXT,
    action TEXT,
    details TEXT,
    log_time DATETIME
)
""")
conn.commit()
cursor.close()
conn.close()
print("Table 'activity_logs' created.")