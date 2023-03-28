import logging
from .utils import Bet


def receive_bet(client_sock):
    """
    Reads bet data from a specific client socket
    """

    # receive message length as uint16 and message of that length
    len = int.from_bytes(client_sock.recv(2), byteorder='big')
    msg = client_sock.recv(len).decode('utf-8').strip()
    addr = client_sock.getpeername()
    logging.info(
        f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')

    return Bet(*msg.split(','))


def respond_bet(client_sock, bet):
    """
    Responds to a client with the bet number
    """
    client_sock.send("{}\n".format(bet.number).encode('utf-8'))
