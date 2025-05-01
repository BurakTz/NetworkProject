import threading
import socket

host = '127.0.0.1' #localhost
port = 55555

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind((host,port))
server.listen()

clients = []
nicknames = []

# Tüm bağlı istemcilere mesaj gönderir.
def broadcast(message):
    for client in clients:
        client.send(message)

# Belirli bir istemci ile iletişimi yönetir.
def handle(client):
    while True:
        try:
            # İstemciden gelen mesajı alır ve tüm istemcilere iletir.
            message = client.recv(1024)
            broadcast(message)
        except:
            # İstemci bağlantısı kesildiğinde, istemciyi listeden çıkarır ve diğer istemcilere bilgi verir.
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f'{nickname} left the chat!'.encode('utf-8'))
            nicknames.remove(nickname)
            break

# Yeni istemci bağlantılarını kabul eder ve her istemci için bir iş parçacığı başlatır.
def receive():
    while True:
        # Yeni bir istemci bağlandığında, istemcinin takma adını alır ve diğer istemcilere bilgi verir.
        client, address = server.accept()
        print(f"Connexted with {str(address)}")

        client.send('NICK'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        nicknames.append(nickname)
        clients.append(client)

        print(f'Nickname of the client is {nickname} !')
        broadcast(f'{nickname} joined the chat!'.encode('utf-8'))
        client.send('Connected to the server !'.encode('utf-8'))

        thread = threading.Thread(target=handle,args=(client,))
        thread.start()

# Sunucunun dinlemeye başladığını belirtir ve istemci bağlantılarını kabul eder.
print('Server is listening...')
receive()
