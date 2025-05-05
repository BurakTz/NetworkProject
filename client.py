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
            if not message:  # Sunucu bağlantıyı kesti mi?
                print("Sunucu bağlantıyı kapattı.")
                break
            print(message)
        except:
            print("Bağlantı kesildi.")
            break
    client.close()
    exit()  # Programı tamamen sonlandır


# Kullanıcıdan mesaj alıp sunucuya gönderen fonksiyon
def write():
    print("- REGISTER <kullanıcı_adı> <şifre> → Yeni hesap oluşturur.")
    print("- LOGIN <kullanıcı_adı> <şifre> → Sisteme giriş yapar.\n")
    while True:
        msg = input()
        client.send(msg.encode('utf-8'))
        if msg.strip().upper() == "EXIT":
            client.shutdown(socket.SHUT_RDWR)  # bağlantıyı çift taraflı kapat
            break


# Alıcı ve gönderici işlemleri aynı anda çalışsın diye thread başlat
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
