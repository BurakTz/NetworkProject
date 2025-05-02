import sqlite3

# Veritabanına bağlan
conn = sqlite3.connect("../db/chat.db")  # db klasörüne göre göreceli yol
cursor = conn.cursor()

# USERS TABLOSU
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nickname TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    status TEXT DEFAULT 'offline',
    last_login DATETIME,
    last_logout DATETIME
);
""")

# PRIVATE_MESSAGES TABLOSU
cursor.execute("""
CREATE TABLE IF NOT EXISTS private_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES users(id),
    FOREIGN KEY (receiver_id) REFERENCES users(id)
);
""")

# GROUP_MESSAGES TABLOSU
cursor.execute("""
CREATE TABLE IF NOT EXISTS group_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER NOT NULL,
    group_name TEXT NOT NULL,
    message TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES users(id)
);
""")

conn.commit()
conn.close()

print("✅ Veritabanı ve tablolar başarıyla oluşturuldu!")
