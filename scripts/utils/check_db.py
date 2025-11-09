import sqlite3
import os

# Check correct database
db_path = r'C:\Users\appia\Desktop\MYBELLA\backend\database\instances\mybella.db'
print(f"Checking database: {db_path}")
print(f"File exists: {os.path.exists(db_path)}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print('\nTables in MYBELLA database:')
for t in tables:
    print(f'  - {t[0]}')

wellness_tables = ['cbt_sessions', 'mood_entries', 'wellness_goals', 'finance_entries', 
                   'social_connections', 'coping_strategies', 'wellness_insights']
                   
print('\nWellness tables exist:')
table_names = [t[0] for t in tables]
for wt in wellness_tables:
    exists = wt in table_names
    print(f'  {wt}: {exists}')
    
conn.close()

# Also check wrong database
wrong_db_path = r'C:\Users\appia\Desktop\backend\database\instances\mybella.db'
print(f'\n\nChecking wrong database: {wrong_db_path}')
print(f'File exists: {os.path.exists(wrong_db_path)}')

if os.path.exists(wrong_db_path):
    conn2 = sqlite3.connect(wrong_db_path)
    cursor2 = conn2.cursor()
    cursor2.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables2 = cursor2.fetchall()
    
    print('\nTables in wrong database:')
    for t in tables2:
        print(f'  - {t[0]}')
    
    table_names2 = [t[0] for t in tables2]
    print('\nWellness tables in wrong database:')
    for wt in wellness_tables:
        exists = wt in table_names2
        print(f'  {wt}: {exists}')
    
    conn2.close()
