import sqlite3
db = sqlite3.connect('t:/heights/documents/projects/streaming_site/templates/userbase.db')
cur = db.cursor()
cur.execute("CREATE TABLE users(username text, password text, about text, age text, sex text, favorite_food text);")