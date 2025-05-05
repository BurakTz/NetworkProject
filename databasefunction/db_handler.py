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

    cursor.execute("SELECT status FROM users WHERE id = ?", (user_id,))
    current_status = cursor.fetchone()[0]

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

def save_private_message(sender_id, receiver_id, message):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO private_messages (sender_id, receiver_id, message)
        VALUES (?, ?, ?)
    """, (sender_id, receiver_id, message))
    conn.commit()
    conn.close()

from datetime import datetime, timedelta
import sqlite3

def get_private_history(user1_id, user2_id):
    conn = sqlite3.connect("db/chat.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sender_id, message, timestamp 
        FROM private_messages
        WHERE (sender_id = ? AND receiver_id = ?)
           OR (sender_id = ? AND receiver_id = ?)
        ORDER BY timestamp ASC
    """, (user1_id, user2_id, user2_id, user1_id))

    messages = []
    for sender_id, message, timestamp in cursor.fetchall():
        # Zamanı UTC'den Türkiye saatine çevir (UTC+3)
        dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S") + timedelta(hours=3)
        local_time = dt.strftime("%d.%m %H:%M")  # Gün.Ay Saat:Dakika
        messages.append((sender_id, message, local_time))

    conn.close()
    return messages


def get_previous_contacts(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT u.nickname
        FROM users u
        JOIN (
            SELECT receiver_id AS user_id FROM private_messages WHERE sender_id = ?
            UNION
            SELECT sender_id AS user_id FROM private_messages WHERE receiver_id = ?
        ) AS chat_users ON chat_users.user_id = u.id
    """, (user_id, user_id))
    results = cursor.fetchall()
    conn.close()
    return [row[0] for row in results]

# Yeni: İstek gönderme
def create_chat_request(sender_id, receiver_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO private_chat_requests (sender_id, receiver_id, status) VALUES (?, ?, 0)",
        (sender_id, receiver_id)
    )
    conn.commit()
    conn.close()

# Yeni: Kabul edilen isteği güncelleme
def accept_chat_request(sender_id, receiver_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE private_chat_requests
        SET status = 1
        WHERE sender_id = ? AND receiver_id = ? AND status = 0
        """,
        (sender_id, receiver_id)
    )
    conn.commit()
    conn.close()

# Yeni: Sohbet hakkı var mı kontrolü
def is_chat_accepted(user1_id, user2_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT accepted FROM chat_relations
        WHERE (user1_id = ? AND user2_id = ?)
           OR (user1_id = ? AND user2_id = ?)
        """,
        (user1_id, user2_id, user2_id, user1_id)
    )
    row = cursor.fetchone()
    conn.close()
    return row and row[0] == 1

def create_or_update_chat_relation(user1_id, user2_id, accepted=1):
    conn = get_connection()
    cursor = conn.cursor()

    # Her iki yönde kontrol et
    cursor.execute("""
        SELECT * FROM chat_relations
        WHERE (user1_id = ? AND user2_id = ?)
           OR (user1_id = ? AND user2_id = ?)
    """, (user1_id, user2_id, user2_id, user1_id))
    result = cursor.fetchone()

    if result:
        cursor.execute("""
            UPDATE chat_relations
            SET accepted = ?
            WHERE (user1_id = ? AND user2_id = ?)
               OR (user1_id = ? AND user2_id = ?)
        """, (accepted, user1_id, user2_id, user2_id, user1_id))
    else:
        cursor.execute("""
            INSERT INTO chat_relations (user1_id, user2_id, accepted)
            VALUES (?, ?, ?)
        """, (user1_id, user2_id, accepted))

    conn.commit()
    conn.close()

def get_user_id_by_nickname(nickname):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE nickname = ?", (nickname,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def logout_user(nickname):
    conn = sqlite3.connect("db/chat.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users 
        SET status = 'offline', 
            last_logout = CURRENT_TIMESTAMP 
        WHERE nickname = ?
    """, (nickname,))
    conn.commit()
    conn.close()
