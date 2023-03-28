import socket
import logging
import signal
import sys
from .utils import store_bets, load_bets, has_won
from .bets import receive_bets, send_msg, receive_msg, respond_winners


class Server:
    def __init__(self, port, listen_backlog, clients):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.clients = int(clients)
        self.client_socks = []
        self.winners = None

        # Define signal handler to gracefully shutdown the server
        signal.signal(signal.SIGINT, self.__signal_handler)
        signal.signal(signal.SIGTERM, self.__signal_handler)

    def __signal_handler(self, signum, stack):
        """
        Signal handler to gracefully shutdown the server
        """
        logging.info(
            f"action: signal_handler | result: success | signal: {signum}")
        self._server_socket.close()
        logging.debug(f'action: close listener socket | result: success')
        for sock in self.client_socks:
            sock.close()
            logging.debug(f'action: close client socket | result: success')

        sys.exit(0)

    def run(self):
        """
        Server loop

        Server that accept a new connections and establishes a communication with a client.
        After client's communication finishes, servers starts to accept new connections again
        """

        while True:
            client_sock = self.__accept_new_connection()
            self.client_socks.append(client_sock)
            self.__handle_client_connection(client_sock)

    def __handle_client_sending_bets(self, client_sock):
        """
        Handle client sending bets in chunks
        """
        try:
            while True:
                bets = receive_bets(client_sock)
                if not bets:
                    break
                store_bets(bets)

                bet_numbers = [bet.number for bet in bets]
                logging.info(
                    f'action: apuestas_almacenadas | result: success | {bet_numbers}')
                send_msg(client_sock, "OK")
        except Exception as e:
            logging.error(
                "action: receive_message | result: fail | error: "+str(e))

            send_msg(client_sock, "ERROR")

    def __set_winners_from_store(self):
        """
        Set raffle winners checking stored bets
        """
        bets = load_bets()
        winners = [bet for bet in bets if has_won(bet)]
        self.winners = winners
        logging.info(
            f'action: set_winners_from_store | result: success | winners: {len(winners)}')

    def __get_winners(self, id):
        """
        Get winners from store for a specific agency
        Winners are only calculated once
        """
        if not self.winners:
            self.__set_winners_from_store()

        # filter lines that start with id
        winners = [bet for bet in self.winners if int(bet.agency) == int(id)]
        return winners

    def __handle_client_asking_for_winner(self, client_sock):
        """
        Handle client asking for winners
        Responding with the winners of the bet if the raffle has already been done
        Else respond with a REFUSE message
        """
        respond_winners(client_sock, self.clients, self.__get_winners)

    def __handle_client_connection(self, client_sock):
        """
        Handle client connection
        Receives a message from the client marking the type of query
        - BETS: client is sending bets
        - ASK: client is asking for winners

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            query_type = receive_msg(client_sock)
            if query_type == 'BETS':
                logging.info('Query: BETS')
                self.__handle_client_sending_bets(client_sock)
            if query_type == 'ASK':
                logging.info('[Query: ASK')
                self.__handle_client_asking_for_winner(client_sock)
        except Exception as e:
            logging.error(
                "action: parse_connection | result: fail | error: "+str(e))
        finally:
            client_sock.close()
            self.client_socks.remove(client_sock)

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        c, addr = self._server_socket.accept()
        logging.info(
            f'action: accept_connections | result: success | ip: {addr[0]}')
        return c
