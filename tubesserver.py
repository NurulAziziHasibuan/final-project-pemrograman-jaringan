import socket
import os
from threading import Thread

serverIP =  '192.168.50.176'
serverPort = 2222

clients = []

# handle client satu dengan client lain
# menerima pesan dan akan dikirim ke client lain
def client_handler(client_socket, client_address):
    while True:
        try:
            data = client_socket.recv(1024).decode("utf-8") 
            if not data:
                remove_client(client_socket)
                break
            
            message_type = data
            if message_type == "file":
                file_extension = client_socket.recv(1024).decode("utf-8")
                file_name = client_socket.recv(1024).decode("utf-8")

                forward_file(client_socket, file_extension, file_name)
            else:
                forward_message(data, client_socket)
        except Exception as e:
            print(f"Error: {e}")
            remove_client(client_socket)
            break

# jika pesan berupa text, pesan akan dikirim ke all client kecuali si sender
def forward_message(message, sender_socket):
    for client_socket in clients:
        if client_socket != sender_socket:
            try:
                client_socket.send("text".encode())
                client_socket.send(message.encode())
            except Exception as e:
                print(f"Error: {e}")
                client_socket.close()
                remove_client(client_socket)

# jika pesan berupa file, pesan akan dikirim ke all client kecuali si sender
def forward_file(sender_socket, file_extension, file_name):
    for client_socket in clients:
        if client_socket != sender_socket:
            try:
                client_socket.send("file".encode())
                client_socket.send(file_extension.encode())
                client_socket.send(file_name.encode())

                file_path = os.path.join("server_files", file_name)
                if os.path.exists(file_path):
                    with open(file_path, "rb") as file:
                        file_data = file.read()
                    client_socket.sendall(file_data)
                else:
                    print(f"File not found: {file_name}")
            except Exception as e:
                print(f"Error: {e}")
                client_socket.close()
                remove_client(client_socket)

# hapus client dari client list dan menutup socket jika client lost connect
def remove_client(client_socket):
    try:
        if client_socket in clients:
            clients.remove(client_socket)
        client_socket.close()
    except Exception as e:
        print(f"Error: {e}")

# start server dan bind ke ip or port dan memulai listening
# setiap ada klien baru, thread baru juga akan dibuat untuk menangani komunikasi client tersebut
def start_server():
    server_socket = socket.socket()
    server_socket.bind((serverIP, serverPort))
    server_socket.listen(5)
    print("Terhubung dengan server {}:{}".format(serverIP, serverPort))

    while True:
        client_socket, client_address = server_socket.accept()
        print("Koneksi berhasil {}".format(client_address))
        clients.append(client_socket)
        client_thread = Thread(target=client_handler, args=(client_socket, client_address))
        client_thread.start()

# fungsi start server
if __name__ == "__main__":
    start_server()
