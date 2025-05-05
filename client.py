import socket
import threading

# Sunucu bilgileri
host = '127.0.0.1'
port = 55555

# Soket oluştur
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

# Global değişken: Dinleme açık mı?
listening = True

# Sunucudan gelen mesajları sürekli dinleyen fonksiyon
def receive():
    global listening
    while listening:
        try:
            message = client.recv(1024).decode('utf-8')
            if not message:
                print("Sunucu bağlantıyı kapattı.")
                break

            print(message)

            if "Ana menüye dönüyorsunuz" in message:
                listening = False
                break

        except:
            print("Bağlantı kesildi.")
            break

    # SADECE EXIT için socket kapatılsın
    if not listening:
        return
    client.close()
    exit()



# Kullanıcıdan mesaj alıp sunucuya gönderen fonksiyon
def write():
    global listening

    print("- REGISTER <kullanıcı_adı> <şifre> → Yeni hesap oluşturur.")
    print("- LOGIN <kullanıcı_adı> <şifre> → Sisteme giriş yapar.\n")

    while True:
        msg = input()
        client.send(msg.encode('utf-8'))

        # Kullanıcı EXIT dediyse bağlantıyı tamamen kes
        if msg.strip().upper() == "EXIT":
            break

        # Kullanıcı DISCONNECT dediyse → receive durdur
        elif msg.strip().upper() == "DISCONNECT":
            listening = False  # receive() duracak
            print("\nOturum sonlandırıldı. Ana menüye dönüyorsunuz...\n")
            print("- REGISTER <kullanıcı_adı> <şifre>")
            print("- LOGIN <kullanıcı_adı> <şifre>\n")
            continue

        # LOGIN sonrası tekrar dinleme başlat
        elif msg.strip().upper().startswith("LOGIN "):
            if not listening:
                listening = True
                threading.Thread(target=receive).start()


# İlk başta thread'leri başlat
threading.Thread(target=receive).start()
write()
