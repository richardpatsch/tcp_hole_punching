import socket
import threading
import time
import sys

from utility import *

SERVER_IP = '0.0.0.0'  # Replace with your server IP
SERVER_PORT = 9001  # Replace with your server port
TIMEOUT = 3
BUFFER_SIZE = 4096


def get_my_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def server_communication(sock, ip, port):
    while True:
        try:
            print("try connecting to {}:{}".format(ip, port))
            sock.connect((ip,port))
        except ConnectionRefusedError:
            print(f"Can't connect to the IP [{sock}:{port}]")
        except OSError:
            print("OSError")
            pass


def client_communication(sock, ip, port):
    try:
        while True:
            try:
                sock.connect((ip, port))
                break
            except socket.error:
                print("Connection Failed, Retrying..")
                time.sleep(2)

        print(f"Connected to the IP [{ip}:{port}]")

        while True:
            data = sock.recv(BUFFER_SIZE)
            if data:
                text_string = data.decode('utf-8')
                divided_packets = text_string.split('END')
                for p in divided_packets:
                    if p != "":
                        print(f'client says: {p}')
                        sock.sendall(get_my_local_ip().encode('utf-8'))

    except ConnectionRefusedError:
        print(f"Can't connect to the IP [{ip}:{port}]")
    except OSError:
        pass


def handle_peer_connection(peer_socket):
    while True:
        try:
            new_connection, client_address = peer_socket.accept()
            print(f"Connected by {client_address}")
            msg = bytes("Hello! This message came from the other client!", encoding='utf-8')
            new_connection.sendall(msg)
        except socket.timeout:
            print("socket.timeout")
            pass


def client():
    other_client_ip = None
    other_client_port = None

    listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listening_socket.bind(('', 0)) # bind to an available port
    listening_socket.listen(1)
    listening_port = listening_socket.getsockname()[1]
    print(f"Listening on port {listening_port}")

    # socket for server communication
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.settimeout(TIMEOUT)

    # socket for client communication
    peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer_socket.settimeout(TIMEOUT)

    # connect to server
    threading.Thread(target=server_communication, args=(server_socket, SERVER_IP, SERVER_PORT,)).start()

    # wait for other client info
    while True:
        try:
            packet = server_socket.recv(BUFFER_SIZE)
            if packet:
                text_string = packet.decode('utf-8')
                divided_packets = text_string.split('END')
                for p in divided_packets:
                    if p != "":
                        print(f'sever says: {p}')
                        server_socket.sendall(get_my_local_ip().encode('utf-8'))

                        if p.startswith('CONNECT'):
                            without_command = p[len('CONNECT '):]
                            client_ip, client_port = without_command.split(',')

                            # build connection
                            print(f"Received cmd to connect to {client_ip}:{client_port}")
                            break
                            threading.Thread(target=client_communication,
                                             args=(client_sock, client_ip, int(client_port),)).start()

        except OSError:
            print("OSError1")
            pass


    print(f"CONNECT TO {other_client_ip}:{other_client_port} now")
    #threading.Thread(target=handle_peer_connection, args=(peer_socket,)).start()


if __name__ == '__main__':
    client()