import json
from helpers import timeout, TimeoutError
from globals import *
from convert import *


class ProxyPlayer(object):
    """
    ProxyPlayer is a Player that communicates requests over TCP to the socket
    given to the init method.
    """

    def __init__(self, socket):
        self.socket = socket

    @timeout(TIMEOUT)
    def get_response(self):
        while(True):
            data = self.socket.recv(MAX_MSG_SIZE)
            if data is not None:
                print("dealer got data: " + str(data))
                return json.loads(data)

    def start(self, player_state, wh):
        """
        Gives the player its state at the beginning of a round. This would allow
        a stateful player to begin to compute possible moves, but since this
        player is not stateful this method does nothing.
        :param player_state: The PlayerState representing this player.
        """
        species = map(lambda spec: Convert.species_to_json(spec), player_state.species)
        cards = map(lambda card: Convert.trait_card_to_json(card), player_state.hand)
        msg = [wh, player_state.food_bag, species, cards]
        print("seding message: " + str(msg))
        self.socket.sendall(json.dumps(msg))

    def choose(self, choice):
        """
        TODO:
        :return: Player's Action choice or False if no actions was selected in
        the timeout period.
        """
        before = map(lambda los: Convert.list_of_species_to_json(los), choice.before)
        after = map(lambda los: Convert.list_of_species_to_json(los), choice.after)
        msg = [before, after]
        self.socket.sendall(json.dumps(msg))
        try:
            data = self.get_response()
            return Convert.json_to_action(data)
        except Exception:
            return False

    def next_feeding(self, player, food_available, opponents):
        """
        Determines a players next feeding species
        :param player: the PlayerState of the player who is feeding
        :param food_available: the amount of food on the watering hole board
        :param opponents: the PlayerStates of other players in the game
        :return: feeding action for the next species to feed, or False if no
        Feeding was selected in the timeout period.
        """
        species = Convert.list_of_species_to_json(player.species)
        opponents_species = map(lambda plr: Convert.list_of_species_to_json(plr.species), opponents)
        cards = map(lambda card: Convert.trait_card_to_json(card), player.hand)
        msg = [player.food_bag, species, cards, food_available, opponents_species]
        print("Sending message:" + str(msg))
        self.socket.sendall(json.dumps(msg))
        try:
            data = self.get_response()
            return Convert.json_to_feeding(data)
        except Exception:
            return False
