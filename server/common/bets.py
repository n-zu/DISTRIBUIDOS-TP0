import logging
from .utils import Bet
from .com import recv_exact, send_all


def receive_msg(client_sock):
    """
    Reads a message from a specific client socket
    """
    len = int.from_bytes(recv_exact(client_sock, 2), byteorder='big')
    msg = recv_exact(client_sock, len).decode('utf-8').strip()
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
        send_all(client_sock, "{}\n".format(response).encode('utf-8'))
    except Exception as e:
        logging.error(
            f'action: send_message | result: fail | error: {str(e)}')


def can_respond_winners(id, clients, finished_clients_lock, raffle_data):
    """
    Verifies if the server can respond to a client
    Taking note of the clients that have already responded
    If all clients have responded, the server can respond to all
    """
    with finished_clients_lock:

        if raffle_data["all_clients_finished"]:
            return True

        if id not in raffle_data["finished_clients"]:
            raffle_data["finished_clients"] = raffle_data["finished_clients"] + [id]

        if len(raffle_data["finished_clients"]) >= clients:
            raffle_data["all_clients_finished"] = True
            logging.info(
                f'action: sorteo | result: success')

    return raffle_data["all_clients_finished"]


def respond_winners(client_sock, clients, get_winners, finished_clients_lock, raffle_data):
    """
    Responds to a client with the winners of the bet
    if the raffle has already been done
    """
    try:
        id = receive_msg(client_sock)

        if can_respond_winners(id, clients, finished_clients_lock, raffle_data):
            winners = get_winners(id)
            winners = stringify_winners(winners)
            send_msg(client_sock, winners)
        else:
            send_msg(client_sock, "REFUSE")
    except Exception as e:
        logging.error(
            f'action: send_message | result: fail | error: {str(e)}')
