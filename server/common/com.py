def recv_exact(socket, length):
    """
    Receive exactly the number of bytes requested from the socket.
    """
    data = b''
    while len(data) < length:
        more = socket.recv(length - len(data))
        if not more:
            raise EOFError('was expecting %d bytes but only received'
                           ' %d bytes before the socket closed'
                           % (length, len(data)))
        data += more
    return data


def send_all(socket, data):
    """
    Send all data to the socket.  Assume the socket is blocking.
    On return, all data has been successfully sent.
    """
    while data:
        sent = socket.send(data)
        data = data[sent:]
