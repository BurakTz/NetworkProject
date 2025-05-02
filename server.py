import socket
import threading
from databasefunction.db_handler import add_user, check_login, update_status
from datetime import datetime

# Sunucu IP ve port ayarları
host = '127.0.0.1'
port = 55555

# Soket oluşturuluyor
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

# Bağlı istemciler tutuluyor
clients = []
user_data = {}  # socket: (id, nickname)
pending_requests = {}
private_chats = {}


# Herkese mesaj gönderen fonksiyon
def broadcast(message, exclude_client=None):
    for client in clients:
        if client != exclude_client:
            try:
                client.send(message.encode('utf-8'))
            except:
                client.close()
                if client in clients:
                    clients.remove(client)

# Her bir istemci için ayrı çalışan işlemci fonksiyon
def handle(client):
    logged_in = False
    user_info = None

    while True:
        try:
            message = client.recv(1024).decode('utf-8')

            # REGISTER
            if message.startswith("REGISTER "):
                _, nickname, password = message.strip().split(" ", 2)
                if add_user(nickname, password):
                    client.send("Kayıt başarılı.\n".encode('utf-8'))
                else:
                    client.send("Bu kullanıcı zaten kayıtlı.\n".encode('utf-8'))

            # LOGIN
            elif message.startswith("LOGIN "):
                _, nickname, password = message.strip().split(" ", 2)
                user = check_login(nickname, password)
                if user:
                    logged_in = True
                    user_info = user
                    user_data[client] = user_info
                    update_status(user[0], "online")
                    client.send(f"Giriş başarılı. Hoş geldin, {nickname}.\n".encode('utf-8'))
                    clients.append(client)
                else:
                    client.send("Giriş başarısız. Kullanıcı adı veya şifre hatalı.\n".encode('utf-8'))

            # SEND (genel mesaj)
            elif message.startswith("SEND ") and logged_in:
                _, content = message.strip().split(" ", 1)
                nickname = user_info[1]
                timestamp = datetime.now().strftime('%H:%M')
                for c in clients:
                    if c != client:
                        c.send(f"[{timestamp}] {nickname}: {content}\n".encode('utf-8'))

            # REQUEST (özel sohbet isteği gönder)
            elif message.startswith("REQUEST ") and logged_in:
                _, target_nick = message.strip().split(" ", 1)
                target_client = None
                for c, u in user_data.items():
                    if u[1] == target_nick:
                        target_client = c
                        break
                if target_client:
                    pending_requests[target_client] = client
                    target_client.send(f"{user_info[1]} sana özel sohbet isteği gönderdi. Kabul için: ACCEPT {user_info[1]}\n".encode('utf-8'))
                    client.send(f"{target_nick} kullanıcısına istek gönderildi.\n".encode('utf-8'))
                else:
                    client.send("Kullanıcı bulunamadı veya bağlı değil.\n".encode('utf-8'))

            # ACCEPT (isteği kabul et)
            elif message.startswith("ACCEPT ") and logged_in:
                _, requester_nick = message.strip().split(" ", 1)
                requester_client = None
                for c, u in user_data.items():
                    if u[1] == requester_nick:
                        requester_client = c
                        break
                if requester_client and pending_requests.get(client) == requester_client:
                    private_chats[client] = requester_client
                    private_chats[requester_client] = client
                    requester_client.send(f"{user_info[1]} isteğini kabul etti. Özel sohbet başladı.\n".encode('utf-8'))
                    client.send("Özel sohbet başladı.\n".encode('utf-8'))
                    del pending_requests[client]
                else:
                    client.send("İstek bulunamadı.\n".encode('utf-8'))

            # PRIVATE (özel mesaj gönder)
            elif message.startswith("PRIVATE ") and logged_in:
                if client in private_chats:
                    _, content = message.strip().split(" ", 1)
                    partner = private_chats[client]
                    sender = user_info[1]
                    timestamp = datetime.now().strftime('%H:%M')
                    partner.send(f"[{timestamp}] (özel) {sender}: {content}\n".encode('utf-8'))
                else:
                    client.send("Şu anda özel bir sohbette değilsiniz.\n".encode('utf-8'))

            # EXIT_PRIVATE
            elif message.strip() == "EXIT_PRIVATE":
                if client in private_chats:
                    partner = private_chats[client]
                    del private_chats[partner]
                    del private_chats[client]
                    client.send("Özel sohbetten çıkıldı.\n".encode('utf-8'))
                    partner.send("Karşı taraf özel sohbetten ayrıldı.\n".encode('utf-8'))
                else:
                    client.send("Aktif özel sohbet yok.\n".encode('utf-8'))

            # EXIT
            elif message.strip() == "EXIT":
                if logged_in and client in clients:
                    update_status(user_info[0], "offline")
                    clients.remove(client)
                client.send("Bağlantı kapatıldı.\n".encode('utf-8'))
                client.close()
                break

            else:
                client.send("Geçersiz komut. Kullan: REGISTER, LOGIN, SEND, REQUEST, ACCEPT, PRIVATE, EXIT_PRIVATE, EXIT\n".encode('utf-8'))

        except Exception as e:
            print(f"Hata: {e}")
            if client in clients:
                clients.remove(client)
            client.close()
            break


# Yeni istemci bağlantılarını sürekli dinleyen fonksiyon
def receive():
    print("Sunucu başlatıldı. Bağlantılar bekleniyor...")
    while True:
        client, address = server.accept()
        print(f"Yeni bağlantı: {address}")
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

# Sunucuyu başlat
receive()
