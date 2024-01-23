
def send_message(socket, text):
    msg = bytes(text + "END", encoding='utf-8')
    socket.sendall(msg)