import json
from helpers import timeout, TimeoutError
from globals import *


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
            if data:
                return data


    def start(self, player_state):
        """
        Gives the player its state at the beginning of a round. This would allow
        a stateful player to begin to compute possible moves, but since this
        player is not stateful this method does nothing.
        :param player_state: The PlayerState representing this player.
        """
        species = map(player_state.species, lambda spec: Convert.species_to_json(spec))
        cards = map(player_state.hand, lambda card: Convert.trait_card_to_json(card))
        msg = [player_state.bag, species, cards]
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
        except (TimeoutError, AssertionError):
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
        opponents_species = map(opponents, lambda plr: Convert.list_of_species_to_json(plr.species))
        cards = map(player.hand, lambda card: Convert.trait_card_to_json(card))
        msg = [player.bag, species, cards, food_available, opponents_species]
        self.socket.sendall(json.dumps(msg))
        try:
            data = self.get_response()
            return Convert.json_to_feeding(data)
        except (TimeoutError, AssertionError):
            return False
