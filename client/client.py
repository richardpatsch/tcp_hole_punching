import socket
import sys
import threading
import time


def attempt_connection(target_info):
    target_ip, target_port = eval(target_info)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
        try:
            soc.connect((target_ip, target_port))
            print(f"Connected to {target_ip}:{target_port}")
            # Here you can add the logic for the connection handling
        except socket.error as e:
            print(f"Connection failed: {e}")


def client(server_ip, server_port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
        soc.connect((server_ip, server_port))
        my_ip, my_port = soc.getsockname()
        print(f"Connected to server with local address {my_ip}:{my_port}")

        # Receiving target client info from server
        target_info = soc.recv(1024).decode('utf-8')
        print(f"Received target client info: {target_info}")

        # Attempt to connect to the other client
        threading.Thread(target=attempt_connection, args=(target_info,)).start()

        # Also listen for incoming connections
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"{my_ip}:{my_port}")
        listener.bind((my_ip, my_port))
        listener.listen(1)
        print(f"Listening for incoming connections on {my_ip}:{my_port}")

        while True:
            try:
                conn, addr = listener.accept()
                print(f"Received connection from {addr}")
                # Here you can add the logic for the connection handling
            except socket.error as e:
                print(f"Listening error: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python client.py <server_ip> <server_port>")
        sys.exit(1)

    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
    client(server_ip, server_port)