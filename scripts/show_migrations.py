import sqlite3
import os
DB = os.path.join(os.path.dirname(__file__), '..', 'db.sqlite3')
DB = os.path.abspath(DB)
print('DB path:', DB)
conn = sqlite3.connect(DB)
c = conn.cursor()
for row in c.execute('SELECT app, name, applied FROM django_migrations ORDER BY app, name'):
    print(row)
conn.close()
