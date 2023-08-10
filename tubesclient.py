import socket
import os
import threading
import time

serverIP =  '192.168.50.176'  # ganti ke ip telkom
serverPort = 2222  # harus beda sama client lain

paragraph_termination = "\n"  # menandai akhir dari paragraf
file_directory = "client_files/"  # direktori untuk menyimpan file
supported_formats = ["jpg", "png", "mp3", "mp4", "docx", "pdf"]  # format yang diterima

# infinite loop mengirim pesan dari klien ke server
def kirim_pesan(handlerSocket: socket.socket):
    while True:
        message = input("Pesan atau nama file yang akan dikirim ('exit' untuk keluar): ")

        if message.lower() == "exit":
            handlerSocket.send("exit".encode())
            break

        if os.path.isfile(message):
            file_name = os.path.basename(message)
            file_extension = file_name.split(".")[-1].lower()

            if file_extension not in supported_formats:
                print("Format tidak didukung.")
                continue

            handlerSocket.send("file".encode())
            handlerSocket.send(file_extension.encode())
            handlerSocket.send(file_name.encode())

            with open(message, "rb") as file:
                file_data = file.read()

            handlerSocket.sendall(file_data)
            print(f"File '{file_name}' berhasil dikirim.")
        else:
            message += paragraph_termination
            handlerSocket.send(message.encode())

# infinite loop menerima pesan dari server
def terima_pesan(handlerSocket: socket.socket):
    current_paragraph = ""
    try:
        while True:
            data = handlerSocket.recv(1024).decode("utf-8")
            if not data:
                break

            # untuk cek tipe pesan text atau file
            message_type = data
            if message_type == "file":
                file_extension = handlerSocket.recv(1024).decode("utf-8")
                file_name = handlerSocket.recv(1024).decode("utf-8")

                # handle duplicate file names
                unique_file_name = get_unique_filename(file_name)

                file_path = os.path.join(file_directory, unique_file_name)

                with open(file_path, "wb") as file:
                    while True:
                        data = handlerSocket.recv(1024)
                        if not data:
                            break
                        file.write(data)

                print(f"File '{unique_file_name}' berhasil diterima dan disimpan di {file_directory}.")
            else:
                current_paragraph += message_type
                while paragraph_termination in current_paragraph:
                    paragraph, current_paragraph = current_paragraph.split(paragraph_termination, 1)
                    print("server: {}".format(paragraph))
    except KeyboardInterrupt:
        print("KeyboardInterrupt detected. Exiting...")
    except Exception as e:
        print(f"An error occurred: {e}")

# generate a unique file name
def get_unique_filename(filename):
    timestamp = int(time.time())
    name, ext = os.path.splitext(filename)
    return f"{name}_{timestamp}{ext}"

# menentukan tipe komunikasi unicast, multicast, atau broadcast
def start_client(communication_type):
    if communication_type == "unicast":
        connectionSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    else:
        connectionSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if communication_type == "broadcast":
            connectionSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    if communication_type != "unicast":
        connectionSocket.bind(('', 0))

    connectionSocket.connect((serverIP, serverPort))
    print("Terhubung dengan server")

    client_thread = threading.Thread(target=terima_pesan, args=(connectionSocket,))
    client_thread.start()

    kirim_pesan(connectionSocket)

# fungsi start client
if __name__ == "__main__":
    for i in range(5):
        communication_type = input("Masukkan tipe komunikasi (unicast/multicast/broadcast): ").lower()
        if communication_type not in ["unicast", "multicast", "broadcast"]:
            print("Tipe komunikasi tidak valid.")
            continue

        start_client(communication_type)
