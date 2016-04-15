from convert import Convert


class ProxyDealer(object):
    possible_next_states = {
        "start": ["choose"],
        "choose": ["feeding", "start"],
        "feeding": ["feeding", "start"]
    }

    def __init__(self, player, connection):
        self.state = "start"
        self.player = player
        self.connection = connection

    def listen_for_messages(self):
        while True:
            try:
                while True:
                    data = self.connection.recv(32)
                    if data:
                        to_send = self.decode(data)
                        if to_send:
                            self.connection.sendall(to_send)
                    else:
                        break
            finally:
                self.connection.close()

    def decode(self, msg):
        decode_start = self.decode_start(msg)
        if decode_start and "start" in possible_next_states[self.state]:
            self.player.start(decode_start)
            self.state = "start"
            return
        decode_choose = self.decode_choose(msg)
        if decode_choose and "choose" in possible_next_states[self.state]:
            choice = self.player.choose(decode_choose)
            self.state = "choose"
            return Convert.action_to_json(choice)
        decode_feeding = self.validate_feeding(msg)
        if decode_feeding and "feeding" in possible_next_states[self.state]:
            # TODO make Feeding class and change Player to take it.
            feeding = self.player.next_feeding(decode_feeding)
            self.state = "feeding"
            return Convert.feeding_to_json(feeding)
        raise Exception

    def decode_start(self, msg):
        # [Natural,[Species+, ..., Species+], Cards] start
        # [LOB,LOB] choose
        # [Natural, [Species+, ..., Species+], Cards, Natural+, LOB] feeding
        try:
            new_state = Convert.json_to_player_state(msg)
        except AssertionError:
            return False

    def decode_choose(self, msg):
        try:
            Convert.json_to_choice(msg)
        except AssertionError:
            return False

    def decode_feeding(self, msg):
        try:
            Convert.json_to_feeding(msg)
        except AssertionError:
            return False
