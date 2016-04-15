import os
import socket
import json
import sys
from evolution.helpers import TimeoutError, timeout
from evolution.globals import *
from evolution.dealer import Dealer
from evolution.proxy_player import ProxyPlayer

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_addr = ('localhost', LISTENING_PORT)
    sock.bind(server_addr)
    sock.listen(1)
    # Wait for a connection
    print >>sys.stderr, 'waiting players'
    connections = []
    try:
        get_player_connections(sock, connections)
    except TimeoutError:
        pass
    print("connections made")
    proxy_players = map(lambda con: ProxyPlayer(con[0]), connections)
    dealer = Dealer(proxy_players)
    dealer.run()
    for connection in connections:
        connection[0].close()

@timeout(PLAYER_CONNECTION_TIME)
def get_player_connections(socket, connections):
    while(len(connections) < MAX_PLAYERS):
        connection, client_addr = socket.accept()
        if connection and client_addr:
            connections.append([connection, client_addr])
            print("player connected")
            connection.sendall("waiting")

if __name__ == "__main__":
    main()
