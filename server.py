import socket
import threading
"""Cоздает многопоточность (мы хотим, чтобы много разных потоков выполнялось одновременно)
хотим получать новые соединения, одновременно обрабатывать 10 клиентских соединений """

HOST = '127.0.0.1'
PORT = 9090

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

server.listen()

clients = []
nicknames = []


# broadcast - широковещательная функция, которая отправляет одно сообщение всем подключенным пользователям
def broadcast(message):
    for client in clients:
        client.send(message)


# handle - функция обработки, обрабатывает отдельные соединения с клиентом
def handle(client):
    while True:
        try:
            # recv(1024) - пытаемся получить сообщение от клиента
            message = client.recv(1024)
            print(f"{nicknames[clients.index(client)]} says {message.decode('utf-8')}")
            broadcast(message)
        except:
            # Если мы получим ошибку (м.б. Клиент просто отключился или вышел из строя) мы удаляем его
            # из списка псевдонимов (nickname) и из списка клиентов и выйдем из цикла
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            nicknames.remove(nickname)
            break


# receive - функция, которая принимает новые соединения и слушает, пока новый клиент не подключится
def receive():
    while True:
        # accept() возвращает адрес клиента и сервера, а затем мы принимаем соединение и у нас есть новый клиент
        client, address = server.accept()
        print(f'Новый пользователь: {str(client)}!')
        print(f'Новый адрес: {str(address)}!')

        # просим клиента ввести никнэйм и принимаем сообщение при помощи метода recv()
        client.send('NICK'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')

        nicknames.append(nickname)
        clients.append(client)

        print(f"Nickname of the client is {nickname}")
        broadcast(f"{nickname} connected to the server!\n".encode('utf-8'))
        # client.send('Connected to the server'.encode('utf-8'))

        # Создаем поток
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


print("Server running...")
# Вызываем метод приёма, он в свою очередь вызывает метод обработки handle, а handle вызывает broadcast
# широковещательный метод
receive()


