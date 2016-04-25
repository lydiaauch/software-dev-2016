from helpers import is_unique_list


class Action(object):
    """
    Describes a Player's action during step 3 of Evolution.
    """

    def __init__(self, food_card, pop_grows, body_grows,
                 species_additions, trait_replacements):
        self.food_card = food_card
        self.pop_grows = pop_grows
        self.body_grows = body_grows
        self.species_additions = species_additions
        self.trait_replacements = trait_replacements

    def __eq__(self, other):
        """Compares two action objects"""
        return all([isinstance(other, Action),
                    self.food_card == other.food_card,
                    self.pop_grows == other.pop_grows,
                    self.body_grows == other.body_grows,
                    self.species_additions == other.species_additions,
                    self.trait_replacements == other.trait_replacements])

    def __str__(self):
        return "food: %d, pop_grows: %s, body_grows: %s, species_additions: %s, trait_replacements: %s" % \
            (self.food_card,
             str(map(lambda x: str(x), self.pop_grows)),
             str(map(lambda x: str(x), self.body_grows)),
             str(map(lambda x: str(x), self.species_additions)),
             str(map(lambda x: str(x), self.trait_replacements)))

    def has_unique_indices(self):
        """
        Checks that the trait card indices used in this action are all unique.
        :return: True if all indices are unique, else False.
        """
        return is_unique_list(self.get_indices())

    def get_indices(self):
        """
        Creates a list of all trait card indices used in this action.
        :return: List of numbers representing the indices of trait cards used by this Action.
        """
        card_indices = [self.food_card]
        card_indices.extend(map(lambda gp: gp.payment_index, self.pop_grows))
        card_indices.extend(map(lambda gb: gb.payment_index, self.body_grows))
        card_indices.extend(map(lambda rt: rt.new_trait_index, self.trait_replacements))
        for board_addition in self.species_additions:
            card_indices.append(board_addition.payment_index)
            card_indices.extend(board_addition.traits)
        return card_indices


class PopGrow(object):
    """
    Describes a Player action to increase the population of the species at the
    specified index using the card at the specified index.
    """

    def __init__(self, species_index, payment_index):
        """
        Constructs a player PopGrow where the card in the player's hand at index
        payment_index is used to increase the population of the species at index
        species_index by one.
        """
        self.species_index = species_index
        self.payment_index = payment_index

    def __eq__(self, other):
        return all([isinstance(other, PopGrow),
                    self.species_index == other.species_index,
                    self.payment_index == other.payment_index])

    def __str__(self):
        return "species_index: %d, payment: %d" % \
            (self.species_index,
             self.payment_index)


class BodyGrow(object):
    """
    Describes a Player action to increase the body of the species at the
    specified index using the card at the specified index.
    """

    def __init__(self, species_index, payment_index):
        """
        Constructs a player BodyGrow where the card in the player's hand at index
        payment_index is used to increase the body of the species at index
        species_index by one.
        """
        self.species_index = species_index
        self.payment_index = payment_index

    def __eq__(self, other):
        return all([isinstance(other, BodyGrow),
                    self.species_index == other.species_index,
                    self.payment_index == other.payment_index])

    def __str__(self):
        return "species_index: %d, payment: %d" %\
            (self.species_index,
             self.payment_index)


class BoardAddition(object):
    """
    Describes a Player action to add a species board to their list to the
    right of their list.
    """

    def __init__(self, payment_index, traits=None):
        """
        Constructs a player BoardAddition where the card in the player's hand
        at index payment_index is used to pay for the species and the indices for
        trait cards to be placed on the species are in the traits list.
        """
        self.payment_index = payment_index
        if not traits:
            self.traits = []
        else:
            self.traits = traits

    def __eq__(self, other):
        return all([isinstance(other, BoardAddition),
                    self.traits == other.traits,
                    self.payment_index == other.payment_index])

    def __str__(self):
        return "payment: %d, traits: %s" % \
            (self.payment_index, str(self.traits))


class ReplaceTrait(object):
    """
    Describes a player action to replace one trait on a species with another.
    """

    def __init__(self, species_index, removed_trait_index, new_trait_index):
        """
        Constructs a ReplaceTrait
        :param species_index: The index of the species to modify in the player's
        list of species.
        :param removed-trait_index: The index of the trait card on the species
        to place this new trait card on.
        :param new_trait_index: The index of the trait in the player's hand of
        the trait card to place on the species.
        """
        self.species_index = species_index
        self.removed_trait_index = removed_trait_index
        self.new_trait_index = new_trait_index

    def __eq__(self, other):
        return all([isinstance(other, ReplaceTrait),
                    self.species_index == other.species_index,
                    self.removed_trait_index == other.removed_trait_index,
                    self.new_trait_index == other.new_trait_index])

    def __str__(self):
        return "species_index: %d, removed_trait: %d, new_trait: %d" % \
            (self.species_index,
             self.removed_trait_index,
             self.new_trait_index)
