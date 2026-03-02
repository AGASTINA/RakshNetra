import sqlite3, os
DB = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'db.sqlite3'))
print('DB:', DB)
conn = sqlite3.connect(DB)
c = conn.cursor()
for row in c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
    print(row[0])
conn.close()
