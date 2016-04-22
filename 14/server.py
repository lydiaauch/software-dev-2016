import socket
import sys
from evolution.helpers import TimeoutError, timeout, print_results
from evolution.globals import *
from evolution.dealer import Dealer
from evolution.proxy_player import ProxyPlayer


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connections = []
    try:
        server_addr = ('localhost', LISTENING_PORT)
        sock.bind(server_addr)
        sock.listen(1)
        # Wait for a connection
        print >> sys.stderr, 'waiting players'
        try:
            get_player_connections(sock, connections)
        except TimeoutError:
            pass
        print("connections made")
        proxy_players = map(lambda con: ProxyPlayer(con[0]), connections)
        dealer = Dealer(proxy_players)
        dealer.run()
        messages = map(lambda connection: connection[2], connections)
        print(print_results(dealer, messages))
    finally:
        for connection in connections:
            print("Closing connection to" + str(connection[1]))
            connection[0].shutdown(socket.SHUT_RDWR)
            connection[0].close()
        print("Closing main socket")
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()


def get_player_connections(socket, connections):
    """
    Waits for at least MIN_PLAYERS to connect and then stops when either
    MAX_PLAYERS are connected or there are more than MIN_PLAYERS connections
    and the timeout has been reached.
    :param socket: TCP socket to listen on.
    :param connections: The list of connections to append the new connection to.
    """
    while(len(connections) < MAX_PLAYERS):
        if len(connections) >= MIN_PLAYERS:
            try:
                connection_with_timout(socket, connections)
            except TimeoutError:
                return
        else:
            connection_no_timeout(socket, connections)


@timeout(PLAYER_CONNECTION_TIME)
def connection_with_timout(socket, connections):
    """
    Adds one connection to the connections list, waiting at most
    PLAYER_CONNECTION_TIME seconds.
    :param socket: TCP socket to listen on.
    :param connections: The list of connections to append the new connection to.
    """
    connection_no_timeout(socket, connections)


def connection_no_timeout(socket, connections):
    """
    Adds one connection to the connections list, waiting as long as needed.
    :param socket: TCP socket to listen on.
    :param connections: The list of connections to append the new connection to.
    """
    connection, client_addr = socket.accept()
    if connection and client_addr:
        msg = connection.recv(MAX_MSG_SIZE)
        connections.append([connection, client_addr, msg])
        print("player connected with message:" + msg)
        connection.sendall("\"ok\"")

if __name__ == "__main__":
    main()
