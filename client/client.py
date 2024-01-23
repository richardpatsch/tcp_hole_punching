import socket
import threading
import time

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
            sock.connect((ip, port))
        except ConnectionRefusedError:
            print(f"Can't connect to the IP [{sock}:{port}]")
        except OSError:
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


def listen_for_connections(sock):
    while True:
        try:
            new_connection, client_address = sock.accept()
            print(f"Connected by {client_address}")
            msg = bytes("Hello! This message came from the other client!", encoding='utf-8')
            new_connection.sendall(msg)
        except socket.timeout:
            print("socket.timeout")
            pass


def client():
    # socket for server communication
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    sock.settimeout(TIMEOUT)


    # socket for client communication
    client_sock = socket.socket()
    client_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    client_sock.settimeout(TIMEOUT)
    client_sock.bind((get_my_local_ip(), SERVER_PORT))
    client_sock.listen(1)

    threading.Thread(target=server_communication, args=(sock, SERVER_IP, SERVER_PORT,)).start()
    threading.Thread(target=listen_for_connections, args=(client_sock,)).start()

    print("test")
    while True:
        try:
            packet = sock.recv(BUFFER_SIZE)
            if packet:
                text_string = packet.decode('utf-8')
                divided_packets = text_string.split('END')
                for p in divided_packets:
                    if p != "":
                        print(f'sever says: {p}')
                        sock.sendall(get_my_local_ip().encode('utf-8'))

                        if p.startswith('CONNECT'):
                            without_command = p[len('CONNECT '):]
                            client_ip, client_port = without_command.split(',')

                            # build connection
                            print(f"Received cmd to connect to {client_ip}:{client_port}")
                            threading.Thread(target=client_communication,
                                             args=(client_sock, client_ip, int(client_port),)).start()

        except OSError:
            pass


if __name__ == '__main__':
    client()