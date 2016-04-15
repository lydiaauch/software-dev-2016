import os
import socket
import json
import sys
from evolution.helpers import TimeoutError, timeout
from globals import *


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_addr = ('localhost', LISTENING_PORT)
    sock.bind(server_addr)
    sock.listen(1)
    while True:
        # Wait for a connection
        print >>sys.stderr, 'waiting players'
        connections = []
        try:
            get_player_connections(sock, connections)
        except TimeoutError:
            pass
        proxy_players = map(connections, lambda con: ProxyPlayer(con[0]))
        dealer = Dealer(proxy_players)
        dealer.run()
        #
        #
        # try:
        #     print >>sys.stderr, 'connection from', client_address
        #     # Receive the data in small chunks and retransmit it
        #     while True:
        #         data = connection.recv(16)
        #         print >>sys.stderr, 'received "%s"' % data
        #         if data:
        #             print >>sys.stderr, 'sending data back to the client'
        #             connection.sendall(data)
        #         else:
        #             print >>sys.stderr, 'no more data from', client_address
        #             break
        #
        finally:
            connection.close()

@timeout(PLAYER_CONNECTION_TIME)
def get_player_connections(socket, connections):
    while(len(connections) < MAX_PLAYERS):
        connection, client_addr = sock.accept()
        if connection and client_addr:
            connections.append([connection, client_addr])
            print("player connected from {}" % client_addr)
            connection.sendall("waiting")

@timeout(1)
def print_loop():
    while(True):
        print("1")
        print("2")
        print("3")


def complete_json(message):
    """
    Determines of a message stub is a complete JSON message
    :param message: string of JSON data
    :return: True if JSON message is complete, else False
    """
    open_identifier_sum = 0
    close_identifier_sum = 0
    start_index = 0
    for i in range(0, len(message)):
        char = message[i]
        if char == MESSAGE_OPEN_IDENTIFIER:
            if start_index == 0:
                start_index = i
            open_identifier_sum += 1
        elif char == MESSAGE_CLOSE_IDENTIFIER:
            close_identifier_sum += 1
        if open_identifier_sum != 0 and close_identifier_sum != 0 and open_identifier_sum == close_identifier_sum:
            return message[start_index:i]



if __name__ == "__main__":
    main()
