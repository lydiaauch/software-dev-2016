import socket
import sys
from evolution.globals import *
from evolution.proxy_dealer import ProxyDealer
from evolution.player import Player

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('localhost', LISTENING_PORT)
print >>sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)

try:
    proxy_dealer = ProxyDealer(Player(), sock)
    proxy_dealer.listen_for_messages()
except Exception:
    print("Closing connection")
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()
