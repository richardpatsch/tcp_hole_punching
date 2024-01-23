import socket
import threading

SERVER_IP = '0.0.0.0'  # Replace with your server IP
SERVER_PORT = 9001  # Replace with your server port
TIMEOUT = 3
BUFFER_SIZE = 1024


class Connection:
    def __init__(self, client_socket, client_address):
        self.client_socket = client_socket
        self.client_address = client_address


def send_message(socket, text):
    msg = bytes(text + "END", encoding='utf-8')
    socket.sendall(msg)


def send_message_to_all(sockets, text):
    for socket in sockets:
        msg = bytes(text + "END", encoding='utf-8')
        socket.sendall(msg)


def server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((SERVER_IP, SERVER_PORT))
    sock.listen(1)

    print('Server listening on {}:{}'.format(SERVER_IP, SERVER_PORT))

    client_addresses = []
    client_connections = []
    connections = []

    while True:
        try:
            new_connection, client_address = sock.accept()
            print(f"New connection from {client_address}")

            # initial hi
            send_message(new_connection, f'hi! (to: {client_address})')

            if len(client_addresses) == 0:
                send_message(new_connection, f'There are no clients connected to the server')

            # send other connected peers to new connection
            for index, address in enumerate(client_addresses):
                send_message(new_connection, f'client {index}: {address}')

            # inform other clients that a new member joined:
            if len(client_connections) > 0:
                send_message_to_all(client_connections, f'client {client_address} has joined the server')

            client_addresses.append(client_address)
            client_connections.append(new_connection)

            connections.append(Connection(new_connection, client_address))

            if len(client_connections) == 2:
                send_message_to_all(client_connections, f'you guys can connect now')
                for i, c in enumerate(connections):
                    other_address = connections[0].client_address if i==0 else connections[1].client_address
                    send_message(c.client_socket, f'CONNECT {other_address[0]},{other_address[1]}')

        except socket.timeout:
            pass


if __name__ == '__main__':
    server()