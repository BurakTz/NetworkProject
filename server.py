
import socket
import threading
import sqlite3
from datetime import datetime
from databasefunction.db_handler import (
    add_user, check_login, update_status,
    save_private_message, get_private_history, get_previous_contacts,
    create_or_update_chat_relation, is_chat_accepted, get_user_id_by_nickname
)

host = '127.0.0.1'
port = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
user_data = {}           # socket: (id, nickname)
active_private_chats = {}  # socket: active_partner_socket

pending_requests = {}    # target_socket: requester_socket

def broadcast(message, exclude=None):
    for client in clients:
        if client != exclude:
            try:
                client.send(message.encode())
            except:
                clients.remove(client)

# Her istemci için mesajları işleyen fonksiyon
# Komutları yorumlar ve işlem yapar

def handle(client):
    logged_in = False
    user_info = None

    while True:
        try:
            message = client.recv(1024).decode().strip()

            # Kullanıcı kaydı
            if message.startswith("REGISTER"):
                try:
                    parts = message.split(" ", 2)
                    if len(parts) != 3:
                        client.send("Hatalı komut. REGISTER <kullanıcı> <şifre>\n".encode())
                        continue
                    _, nick, pwd = parts
                    if add_user(nick, pwd):
                        client.send("Kayıt başarılı.\n".encode())
                    else:
                        client.send("Bu kullanıcı zaten var.\n".encode())
                except:
                    client.send("Hatalı komut. REGISTER ali 1234\n".encode())

            # Kullanıcı girişi
            elif message.startswith("LOGIN"):
                try:
                    parts = message.split(" ", 2)
                    if len(parts) != 3:
                        client.send("LOGIN komutu hatalı. LOGIN <kullanıcı> <şifre>\n".encode())
                        continue
                    _, nick, pwd = parts
                    user = check_login(nick, pwd)
                    if user:
                        logged_in = True
                        user_info = user
                        user_data[client] = user_info
                        update_status(user[0], "online")
                        if client not in clients:
                            clients.append(client)

                        client.send(f"Hoş geldin, {nick}.\n".encode())
                        client.send(
                            "\nKullanabileceğin komutlar:\n"
                            "- WHO → Şu anda online olan kullanıcıları listeler. Örnek: WHO\n"
                            "- SEND <mesaj> → Genel sohbete mesaj gönderir. Örnek: SEND Merhaba herkese!\n"
                            "- REQUEST <kullanıcı> → Belirtilen kullanıcıya özel sohbet isteği yollar. Örnek: REQUEST ahmet\n"
                            "- ACCEPT <kullanıcı> → Gelen özel sohbet isteğini kabul eder. Örnek: ACCEPT ahmet\n"
                            "- OPEN CHAT <kullanıcı> → Önceden onayladığınız biriyle özel sohbeti başlatır. Örnek: OPEN CHAT ahmet\n"
                            "- PRIVATE SEND <mesaj> → Aktif özel sohbet içindeki kullanıcıya mesaj gönderir. Örnek: PRIVATE SEND selam naber\n"
                            "- CLOSE CHAT → Açık olan özel sohbeti kapatır.\n"
                            "- DISCONNECT → Oturumdan çıkış yapar, ana menüye döner. Bağlantı kapanmaz.\n"
                            "- EXIT → Sistemden tamamen çıkar ve bağlantıyı kapatır.\n".encode()
                        )

                        # Geçmiş chatler gösteriliyor
                        contacts = get_previous_contacts(user[0])
                        if contacts:
                            client.send("\nGeçmiş Chatler:\n".encode())
                            for name in contacts:
                                conn = sqlite3.connect("db/chat.db")
                                cursor = conn.cursor()
                                cursor.execute("SELECT status FROM users WHERE nickname = ?", (name,))
                                row = cursor.fetchone()
                                conn.close()
                                durum = "(online)" if row and row[0] == "online" else "(offline)"
                                client.send(f"- {name} {durum}\n".encode())
                        else:
                            client.send("\nHiç özel sohbet yapılmamış.\n".encode())

                    else:
                        client.send("Giriş başarısız.\n".encode())
                except:
                    client.send("LOGIN komutu hatalı.\n".encode())

            # Genel sohbete mesaj gönderme
            elif message.startswith("SEND ") and logged_in:
                content = message[5:]
                sender = user_info[1]
                timestamp = datetime.now().strftime("%H:%M")
                for c in clients:
                    if c != client:
                        c.send(f"[{timestamp}] {sender}: {content}\n".encode())
                client.send("Mesaj gönderildi.\n".encode())

            # Özel sohbet isteği gönderme
            elif message.startswith("REQUEST ") and logged_in:
                parts = message.split(" ", 1)
                if len(parts) != 2:
                    client.send("Hatalı kullanım. Örnek: REQUEST ahmet\n".encode())
                    continue
                _, target_nick = parts
                if target_nick == user_info[1]:
                    client.send("Kendine istek gönderemezsin.\n".encode())
                    continue
                for c, u in user_data.items():
                    if u[1] == target_nick:
                        pending_requests[c] = client
                        c.send(f"{user_info[1]} sana özel sohbet isteği gönderdi. ACCEPT {user_info[1]}\n".encode())
                        client.send("İstek gönderildi.\n".encode())
                        break
                else:
                    client.send("Kullanıcı bulunamadı.\n".encode())

            # Özel sohbet isteği kabulü
            elif message.startswith("ACCEPT ") and logged_in:
                try:
                    _, requester_nick = message.split(" ", 1)
                    for c, u in user_data.items():
                        if u[1] == requester_nick and pending_requests.get(client) == c:
                            create_or_update_chat_relation(user_info[0], u[0], 1)
                            create_or_update_chat_relation(u[0], user_info[0], 1)  # ↔ iki yönlü ekle
                            client.send("İstek kabul edildi. OPEN CHAT komutunu kullanabilirsiniz.\n".encode())
                            c.send(
                                f"{user_info[1]} isteğini kabul etti. OPEN CHAT komutu ile sohbet başlatabilirsin.\n".encode())
                            del pending_requests[client]
                            break
                    else:
                        client.send("İstek bulunamadı.\n".encode())
                except Exception as e:
                    print(f"ACCEPT hatası: {e}")
                    client.send("ACCEPT sırasında bir hata oluştu.\n".encode())



            # Geçmiş özel sohbetleri görme ve yeniden başlatma
            elif message.startswith("OPEN CHAT ") and logged_in:
                parts = message.split(" ", 2)
                if len(parts) != 3:
                    client.send("Hatalı kullanım. Örnek: OPEN CHAT ahmet\n".encode())
                    continue
                _, _, target_nick = parts
                target_id = get_user_id_by_nickname(target_nick)
                if not target_id:
                    client.send("Kullanıcı bulunamadı.\n".encode())
                    continue
                if is_chat_accepted(user_info[0], target_id):
                    for c, u in user_data.items():
                        if u[0] == target_id:
                            active_private_chats[client] = c
                            break
                    else:
                        active_private_chats[client] = target_nick
                    history = get_private_history(user_info[0], target_id)
                    client.send(f"\n{target_nick} ile geçmiş mesajların:\n".encode())
                    for sender_id, msg, time in history:
                        sender = user_info[1] if sender_id == user_info[0] else target_nick
                        client.send(f"[{time}] {sender}: {msg}\n".encode())
                else:
                    client.send("Bu kullanıcı ile onaylanmış sohbetiniz yok.\n".encode())

            # Özel mesaj gönderme
            elif message.startswith("PRIVATE SEND ") and logged_in:
                parts = message.split(" ", 2)
                if len(parts) != 3:
                    client.send("Hatalı kullanım. Örnek: PRIVATE SEND mesaj\n".encode())
                    continue
                _, _, content = parts
                partner = active_private_chats.get(client)

                if not partner:
                    client.send("Aktif özel sohbet yok. Önce OPEN CHAT kullan.\n".encode())
                    continue

                # Alıcının ID'sini belirle
                if isinstance(partner, socket.socket):
                    receiver_id = user_data[partner][0]
                else:
                    receiver_id = get_user_id_by_nickname(partner)

                if receiver_id:
                    # Veritabanına kaydet (her zaman)
                    save_private_message(user_info[0], receiver_id, content)

                    # Eğer karşı taraf online ve socket varsa gönder
                    for c, u in user_data.items():
                        if u[0] == receiver_id:
                            try:
                                c.send(f"(özel) {user_info[1]}: {content}\n".encode())
                            except:
                                pass  # mesaj veritabanına kaydedildi zaten
                            break

                    timestamp = datetime.now().strftime("%H:%M")
                    client.send(f"(özel) mesaj gönderildi. [{timestamp}]\n".encode())

                else:
                    client.send("Alıcı bulunamadı.\n".encode())


            # Özel sohbeti kapatma
            elif message.strip().upper() == "CLOSE CHAT" and logged_in:
                if client in active_private_chats:
                    del active_private_chats[client]
                    client.send("Özel sohbet kapatıldı.\n".encode())
                else:
                    client.send("Aktif özel sohbet yok.\n".encode())

            # Özel sohbetteki kullanıcıların onnlıne offlıne olma durumunu duzenler
            elif message.strip().upper() == "CHAT DURUM YENILE" and logged_in:
                contacts = get_previous_contacts(user_info[0])
                if contacts:
                    client.send("\nGeçmişte sohbet ettiğiniz kullanıcılar (durumları güncellenmiştir):\n".encode())
                    for name in contacts:
                        conn = sqlite3.connect("db/chat.db")
                        cursor = conn.cursor()
                        cursor.execute("SELECT status FROM users WHERE nickname = ?", (name,))
                        row = cursor.fetchone()
                        conn.close()
                        durum = "(online)" if row and row[0] == "online" else "(offline)"
                        client.send(f"- {name} {durum}\n".encode())
                else:
                    client.send("\nDaha önce özel sohbet yaptığınız bir kullanıcı bulunmamaktadır.\n".encode())


            # Oturumu kapat ama bağlantıyı kesme
            elif message.strip().upper() == "DISCONNECT" and logged_in:
                update_status(user_info[0], "offline")
                client.send("Bağlantı sonlandırıldı. Ana menüye dönüyorsunuz...\n".encode())
                logged_in = False
                user_info = None
                if client in active_private_chats:
                    del active_private_chats[client]

            # Oturum sonlandırma
            elif message.strip().upper() == "EXIT":
                if logged_in:
                    update_status(user_info[0], "offline")
                if client in clients:
                    clients.remove(client)
                if client in user_data:
                    del user_data[client]
                if client in active_private_chats:
                    del active_private_chats[client]
                client.send("Çıkış yapıldı.\n".encode())
                client.close()
                break

            else:
                client.send("Geçersiz komut.\n".encode())

        except Exception as e:
            print(f"HATA: {e}")
            if client in clients:
                clients.remove(client)
            if client in user_data:
                del user_data[client]
            if client in active_private_chats:
                del active_private_chats[client]
            client.close()
            break

# Yeni bağlantıları kabul eden sunucu döngüsü
def receive():
    print("[Sunucu başlatıldı] Dinleniyor...")
    while True:
        client, addr = server.accept()
        print(f"Bağlantı geldi: {addr}")
        threading.Thread(target=handle, args=(client,)).start()

receive()
