import sqlite3

conn = sqlite3.connect("../db/chat.db")
cursor = conn.cursor()

cursor.execute("DELETE FROM private_messages;")
cursor.execute("DELETE FROM group_messages;")
cursor.execute("DELETE FROM users;")

conn.commit()
conn.close()

print("Tablo içerikleri temizlendi!")
