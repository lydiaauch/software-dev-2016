import os
import socket
import json
import sys

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_addr = ('localhost', 10000)
    sock.bind(server_addr)
    sock.listen(1)
    while True:
        # Wait for a connection
        print >>sys.stderr, 'waiting for a connection'
        connection, client_address = sock.accept()
        try:
            print >>sys.stderr, 'connection from', client_address

            # Receive the data in small chunks and retransmit it
            while True:
                data = connection.recv(16)
                print >>sys.stderr, 'received "%s"' % data
                if data:
                    print >>sys.stderr, 'sending data back to the client'
                    connection.sendall(data)
                else:
                    print >>sys.stderr, 'no more data from', client_address
                    break

        finally:
            # Clean up the connection
            connection.close()

    # sock = socket.create_connection((SERVER_ADDRESS, PORT))
    # player = Player()
    # try:
    #     message = ""
    #     while True:
    #         message += sock.recv(BUFFSIZE)
    #         complete_message = complete_json(message)
    #         if complete_message:
    #             response = handle_message(player, complete_message)
    #             sock.sendall(response)
    #             message = ""
    # finally:
    #     sock.close()


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
