import logging
from .utils import Bet


def receive_msg(client_sock):
    """
    Reads a message from a specific client socket
    """
    len = int.from_bytes(client_sock.recv(2), byteorder='big')
    msg = client_sock.recv(len).decode('utf-8').strip()
    addr = client_sock.getpeername()
    logging.info(
        f'action: receive_message | result: success | ip: {addr[0]}')

    return msg


def parse_bet(bet):
    """
    Parses a string with a single bet
    which is a comma separated list of fields
    """
    bet = bet.split(',')
    bet = [field.strip() for field in bet]
    return Bet(*bet)


def parse_bets(bets):
    """
    Parses a string with multiple bets separated by ';'
    """
    bets = bets.split(';')
    bets = filter(lambda line: line != '', bets)

    return [parse_bet(bet) for bet in bets]


def stringify_winners(bets):
    """
    Converts a list of bets to a string with the
    document numbers of the bets separated by commas
    """
    winners = [bet.document for bet in bets]
    winners = ','.join(winners)
    return winners


def receive_bets(client_sock):
    """
    Reads bet data from a specific client socket
    """

    msg = receive_msg(client_sock)

    if msg == 'CLOSE':
        return None

    return parse_bets(msg)


def send_msg(client_sock, response):
    """
    Sends a response to a specific client socket
    """
    try:
        client_sock.send("{}\n".format(response).encode('utf-8'))
    except Exception as e:
        logging.error(
            f'action: send_message | result: fail | error: {str(e)}')


finished_clients = set()
all_clients_finished = False


def can_respond_winners(id, clients):
    """
    Verifies if the server can respond to a client
    Taking note of the clients that have already responded
    If all clients have responded, the server can respond to all
    """
    global finished_clients
    global all_clients_finished

    if all_clients_finished:
        return True

    finished_clients.add(id)

    if len(finished_clients) >= clients:
        all_clients_finished = True
        logging.info(
            f'action: sorteo | result: success')

    return all_clients_finished


def respond_winners(client_sock, clients, get_winners):
    """
    Responds to a client with the winners of the bet
    if the raffle has already been done
    """
    try:
        id = receive_msg(client_sock)

        if can_respond_winners(id, clients):
            winners = get_winners(id)
            winners = stringify_winners(winners)
            send_msg(client_sock, winners)
        else:
            client_sock.send("{}\n".format("REFUSE").encode('utf-8'))
    except Exception as e:
        logging.error(
            f'action: send_message | result: fail | error: {str(e)}')
