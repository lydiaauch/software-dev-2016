class PlayerState(object):
    """
    Represents data about the player that is kept track of by the dealer
    in order to prevent the player from modifying their data or acting out of turn
    the dealer only sends the minimum amount of data needed for the player to make
    choices

    Attributes:
        name: An Integer identifier for the player.
        food_bag: An Integer representing the number of food tokens acquired.
        hand: A List of `TraitCards` representing the cards the player can use.
        species: A List of `Species` representing the species boards the player
            has in front of them. Species are ordered from left to right.


    """
    def __init__(self, name=None, food_bag=None, hand=None, species=None):
        if food_bag is None:
            food_bag = 0
        if hand is None:
            hand = []
        if species is None:
            species = []

        self.name = name
        self.food_bag = food_bag
        self.hand = hand
        self.species = species

    def __str__(self):
        return "PlayerState(Food=%d, Hand=%s, Species=%s" % (self.food_bag, self.hand, self.species)

    def __eq__(self, other):
        return all([isinstance(other, PlayerState),
                    self.name == other.name,
                    self.food_bag == other.food_bag,
                    self.hand == other.hand,
                    self.species == other.species])
