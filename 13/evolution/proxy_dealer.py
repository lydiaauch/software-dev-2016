import json
from convert import Convert

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

    def listen_for_messages(self):
        while True:
            try:
                while True:
                    data = self.connection.recv(1024)
                    if data is not None:
                        print("Got data: " + str(data))
                        to_send = self.decode(data)
                        if to_send is not None:
                            self.connection.sendall(json.dumps(to_send))
                    else:
                        break
            finally:
                self.connection.close()

    def decode(self, msg):
        if msg == "waiting":
            return
        msg = json.loads(msg)
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
