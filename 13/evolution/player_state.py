from species import Species
from actions import *

class PlayerState(object):
    """
    Represents data about the player that is kept track of by the dealer
    in order to prevent the player from modifying their data or acting out of turn
    the dealer only sends the minimum amount of data needed for the player to make
    choices

    Attributes:
        name: An Integer identifier for the player.
        food_bag: Integer representing the number of food tokens acquired.
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

    def apply_action(self, action):
        """
        Applies all parts of the given action to this player state.
        :param action: An Action to apply.
        """
        self.create_new_boards(action.species_additions)
        self.replace_traits(action.trait_replacements)
        self.increase_populations(action.pop_grows)
        self.increase_body_sizes(action.body_grows)
        self.remove_used_cards()

    def create_new_boards(self, board_additions):
        """
        Creates new Species for each BoardAddition in the given list of additions.
        :param board_additions: List of BoardAdditions to construct species from.
        """
        for addition in board_additions:
            self.hand[addition.payment_index].used = True
            traits = []
            for trait_idx in addition.traits:
                new_trait = self.hand[trait_idx]
                traits.append(new_trait)
                new_trait.used = True
            self.species.append(Species(traits=traits))


    def replace_traits(self, trait_replacements):
        """
        Swaps out traits as described in the list of ReplaceTraits.
        :param trait_replacements: The list of ReplaceTrait to use.
        """
        for replace in trait_replacements:
            species = self.species[replace.species_index]
            new_trait = self.hand[replace.new_trait_index]
            species.traits[replace.removed_trait_index] = new_trait
            new_trait.used = True

    def increase_populations(self, pop_grows):
        """
        Increases the population by one for each speices described in the given
        list of PopGrow.
        :param pop_grows: List of PopGrow representing species whose population
        should be increased.
        """
        for grow in pop_grows:
            species = self.species[grow.species_index]
            species.population += 1
            self.hand[grow.payment_index].used = True

    def increase_body_sizes(self, body_grows):
        """
        Increases the body size by one for each speices described in the given
        list of BodyGrow.
        :param body_grows: List of BodyGrow representing species whose body size
        should be increased.
        """
        for grow in body_grows:
            species = self.species[grow.species_index]
            species.body += 1
            self.hand[grow.payment_index].used = True

    def remove_used_cards(self):
        """
        Removes all cards from this player's hand that are marked used.
        """
        self.hand = filter(lambda c: not c.used, self.hand)

    def public_state(self):
        """
        Creates a new player with private information set to defaults.
        :return: A new PlayerState object with the same information as this
        player state, but with private information set to defaults.
        """
        return PlayerState(name=self.name, food_bag=None, hand=None, species=self.species)
