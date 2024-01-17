import socket
import threading


def handle_client(client_socket, client_info, other_client_info):
    try:
        # Send other client's address to the current client
        client_socket.sendall(str(other_client_info).encode('utf-8'))
    finally:
        client_socket.close()


def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 9000))
    server_socket.listen(2)

    print("Server listening on port 9000")

    while True:
        client_socket, client_addr = server_socket.accept()
        print(f"Received connection from {client_addr}")

        other_client_socket, other_client_addr = server_socket.accept()
        print(f"Received connection from {other_client_addr}")

        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_addr, other_client_addr))
        other_client_thread = threading.Thread(target=handle_client, args=(other_client_socket, other_client_addr, client_addr))

        client_thread.start()
        other_client_thread.start()


if __name__ == "__main__":
    server()