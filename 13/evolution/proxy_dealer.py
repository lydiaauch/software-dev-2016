import json
from convert import Convert
from helpers import timeout


possible_next_states = {
    "waiting": ["start"],
    "start": ["choose"],
    "choose": ["feeding", "start"],
    "feeding": ["feeding", "start"]
}


class ProxyDealer(object):
    def __init__(self, player, connection):
        self.state = "waiting"
        self.player = player
        self.connection = connection

    @timeout(20)
    def listen_for_messages(self):
        while True:
            data = self.connection.recv(1024)
            print("Got data: " + str(data))
            while data is not None:
                (msg, data) = self.json_parser(data)
                print("Parsed message: " + str(msg))
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
        if msg == "ok":
            return
        decode_start = self.decode_start(msg)
        if "feeding" in possible_next_states[self.state] and len(msg) == 5:
            # TODO make Feeding class and change Player to take it.
            player = Convert.json_to_player_state(msg[0:3])
            print("Choosing feeding")
            opponents = Convert.json_to_listof_listof_species(msg[4])
            feeding = self.player.next_feeding(player, msg[3], opponents)
            self.state = "feeding"
            print(Convert.feeding_to_json(feeding))
            return Convert.feeding_to_json(feeding)
        if decode_start and "start" in possible_next_states[self.state]:
            print("Got start message")
            self.player.start(decode_start)
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
        # [Natural,[Species+, ..., Species+], Cards] start
        # [LOB,LOB] choose
        # [Natural, [Species+, ..., Species+], Cards, Natural+, LOB] feeding
        try:
            return Convert.json_to_player_state(msg)
        except Exception:
            return False

    def decode_choose(self, msg):
        try:
            return Convert.json_to_choice(msg)
        except Exception:
            return False

    def decode_feeding(self, msg):
        try:
            return Convert.json_to_feeding(msg)
        except Exception:
            return False

    def validate_feeding(self, msg):
        # TODO
        return True
