import socket
import logging
import signal
import sys
from .utils import store_bets
from .bets import receive_bets, send_msg, receive_msg, respond_winners


class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.clients = []

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
        for client in self.clients:
            client.close()
            logging.debug(f'action: close client socket | result: success')

        sys.exit(0)

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a communication with a client.
        After client's communication finishes, servers starts to accept new connections again
        """

        while True:
            client_sock = self.__accept_new_connection()
            self.clients.append(client_sock)
            self.__handle_client_connection(client_sock)

    def __handle_client_sending_bets(self, client_sock):
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

    def __handle_client_asking_for_winner(self, client_sock):
        respond_winners(client_sock)

    def __handle_client_connection(self, client_sock):
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
            self.clients.remove(client_sock)

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
