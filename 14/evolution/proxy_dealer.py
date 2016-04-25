import json
from convert import Convert
from helpers import timeout
from globals import *


possible_next_states = {
    "waiting": ["start"],
    "start": ["choose"],
    "choose": ["feeding", "start"],
    "feeding": ["feeding", "start"]
}


class ProxyDealer(object):
    """
    A ProxyDealer object to convert local Dealer interactions with the player
    to a TCP JSON message and handles timing protocol between the server and client
    """
    def __init__(self, player, connection):
        self.state = "waiting"
        self.player = player
        self.connection = connection

    @timeout(CLIENT_WAIT_TIME)
    def listen_for_messages(self):
        """
        Waits for a message from the Dealer for CLIENT_WAIT_TIME seconds.
        """
        while True:
            data = self.connection.recv(1024)
            print("Got data: " + str(data))
            while data is not None:
                (msg, data) = self.json_parser(data)
                to_send = self.decode(msg)
                print("Remaining msg in buffer: " + str(data))
                if to_send is not None:
                    self.connection.sendall(json.dumps(to_send))

    def json_parser(self, buffer):
        """
        Searches for full JSON messages and adds incomplete messages to a buffer
        :param buffer: the JSON messages
        :return: a tuple of (JSON_message, current buffer) where the message is the
        first complete JSON element in the buffer
        """
        (json_obj, end_index) = json.JSONDecoder().raw_decode(buffer)
        buffer = buffer[end_index:]
        if buffer == "":
            buffer = None
        return (json_obj, buffer)

    def decode(self, msg):
        """
        Decides which type of message the server has sent and verifies that the
        timing of the message is valid and communicates to the player if the
        message is valid.
        :param msg: the message from the server to decode.
        :return: the message to send to the Dealer, if any.
        """
        if msg == "ok":
            return
        if "feeding" in possible_next_states[self.state] and len(msg) == 5:
            player = Convert.json_to_player_state(msg[0:3])
            opponents = Convert.json_to_listof_listof_species(msg[4])
            feeding = self.player.next_feeding(player, msg[3], opponents)
            self.state = "feeding"
            return Convert.feeding_to_json(feeding)
        (player, wh) = self.decode_start(msg)
        if player and "start" in possible_next_states[self.state]:
            print("Got start message")
            self.player.start(player, wh)
            self.state = "start"
            return
        decode_choose = self.decode_choose(msg)
        if decode_choose and "choose" in possible_next_states[self.state]:
            print("Choosing action")
            choice = self.player.choose(decode_choose)
            self.state = "choose"
            return Convert.action_to_json(choice)
        raise Exception

    def decode_start(self, msg):
        """
        Attempts to decode the given msg into a tuple (player, watering_hole)
        :param msg: The JSON message to decode.
        :return: The tuple (PlayerState, Int) representing the player and the
        food in the watering hole, or (False, False) if the conversion fails.
        """
        try:
            assert(isinstance(msg[0], int))
            return (Convert.json_to_player_state(msg[1:]), msg[0])
        except Exception:
            return (False, False)

    def decode_json(self, msg, conv_func):
        """
        Attempts to decode the json msg using the given conversion function
        conv_func. If the conversion fails, returns False.
        :param msg: The JSON message to convert.
        :param conv_func: The function to use to convert the JSON.
        :return: the converted message or False if the conversion failed. 
        """
        try:
            return conv_func(msg)
        except Exception:
            return False

    def decode_choose(self, msg):
        """
        Attempts to convert the message to a Choose type.
        :param msg: The JSON message to convert.
        """
        self.decode_json(msg, Convert.json_to_choice)

    def decode_feeding(self, msg):
        """
        Attempts to convert the message to a Feeding type.
        :param msg: The JSON message to convert.
        """
        self.decode_json(msg, Convert.json_to_feeding)
