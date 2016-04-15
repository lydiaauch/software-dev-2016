class ProxyPlayer(object):
    """
    ProxyPlayer is a Player that communicates requests over TCP to the socket
    given to the init method.
    """

    def __init__(self, socket):
        self.socket = socket

    @timeout(TIMEOUT)
    def get_response(cls):
        while(True):
            data = connection.recv(MAX_MSG_SIZE)
            if data:
                return data


    def start(cls, player_state):
        """
        Gives the player its state at the beginning of a round. This would allow
        a stateful player to begin to compute possible moves, but since this
        player is not stateful this method does nothing.
        :param player_state: The PlayerState representing this player.
        """
        species = map(player_state.species, lambda spec: Convert.species_to_json(spec))
        cards = map(player_state.hand, lambda card: Convert.trait_card_to_json(card))
        msg = [player_state.bag, species, cards]
        socket.sendall(Json.dumps(msg))

    def choose(cls, choice):
        """
        TODO:
        :return: Player's Action choice or False if no actions was selected in
        the timeout period.
        """

        before = map(choice.before, lambda los: Convert.list_of_species_to_json(los))
        after = map(choice.after, lambda los: Convert.list_of_species_to_json(los))
        msg = [before, after]
        socket.sendall(Json.dumps(msg))
        try:
            data = self.get_response()
            return Convert.json_to_action(data)
        except (TimeoutError, AssertionError):
            return False

    def next_feeding(cls, player, food_available, opponents):
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
        socket.sendall(Json.dumps(msg))
        try:
            data = self.get_response()
            return Convert.json_to_feeding(data)
        except (TimeoutError, AssertionError):
            return False
