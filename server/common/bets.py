import logging
from .utils import Bet


def receive_msg(client_sock):
    # receive message length as uint16 and message of that length
    len = int.from_bytes(client_sock.recv(2), byteorder='big')
    msg = client_sock.recv(len).decode('utf-8').strip()
    addr = client_sock.getpeername()
    logging.info(
        f'action: receive_message | result: success | ip: {addr[0]}')

    return msg


def parse_bet(bet):
    bet = bet.split(',')
    bet = [field.strip() for field in bet]
    return Bet(*bet)


def parse_bets(bets):
    bets = bets.split(';')
    bets = filter(lambda line: line != '', bets)

    return [parse_bet(bet) for bet in bets]


def receive_bets(client_sock):

    msg = receive_msg(client_sock)

    if msg == 'CLOSE':
        return None

    return parse_bets(msg)


def send_msg(client_sock, response):
    try:
        client_sock.send("{}\n".format(response).encode('utf-8'))
    except Exception as e:
        logging.error(
            f'action: send_message | result: fail | error: {str(e)}')


def respond_winners(client_sock):
    try:
        client_sock.send("{}\n".format("TODO").encode('utf-8'))
    except Exception as e:
        logging.error(
            f'action: send_message | result: fail | error: {str(e)}')
