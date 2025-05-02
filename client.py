import socket
import threading

# Sunucu bilgileri
host = '127.0.0.1'
port = 55555

# Soket oluştur
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

# Sunucudan gelen mesajları sürekli dinleyen fonksiyon
def receive():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            print(message)
        except:
            print("Bağlantı kesildi.")
            client.close()
            break

# Kullanıcıdan mesaj alıp sunucuya gönderen fonksiyon
def write():
    while True:
        msg = input()
        client.send(msg.encode('utf-8'))
        if msg.strip().upper() == "EXIT":
            break

# Alıcı ve gönderici işlemleri aynı anda çalışsın diye thread başlat
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
