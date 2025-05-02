import sqlite3
from datetime import datetime

def get_connection():
    return sqlite3.connect("db/chat.db")

# Yeni kullanıcı ekle
def add_user(nickname, password):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (nickname, password, status, last_login) VALUES (?, ?, ?, ?)",
                       (nickname, password, 'offline', datetime.now()))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# Kullanıcıyı giriş bilgisiyle kontrol et
def check_login(nickname, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE nickname = ? AND password = ?", (nickname, password))
    user = cursor.fetchone()
    conn.close()
    return user

def update_status(user_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now()

    # Şu anki durumu öğren
    cursor.execute("SELECT status FROM users WHERE id = ?", (user_id,))
    current_status = cursor.fetchone()[0]

    # Eğer zaten o durumdaysa işlem yapma
    if current_status == status:
        print(f"Zaten '{status}' durumundasın.")
        conn.close()
        return False

    if status == "offline":
        cursor.execute("""
            UPDATE users
            SET status = ?, last_logout = ?
            WHERE id = ?
        """, (status, now, user_id))
    else:
        cursor.execute("""
            UPDATE users
            SET status = ?, last_login = ?
            WHERE id = ?
        """, (status, now, user_id))

    conn.commit()
    conn.close()


# Kullanıcıyı çıkış yaptıktan sonra offline olarak görünsün
def logout_user(nickname):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Kullanıcının ID'sini bul
        cursor.execute("SELECT id FROM users WHERE nickname = ?", (nickname,))
        user = cursor.fetchone()
        if user:
            update_status(user[0],"offline")
            return True
        else:
            return False
    except:
        return False
    finally:
        conn.close()
