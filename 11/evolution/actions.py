class Action(object):
    """
    Describes a Player's action during step 3 of Evolution.
    """

    def __init__(self, species_index, board_additions, trait_replacements):
        self.species_index = species_index
        self.board_additions = board_additions
        self.trait_replacements = trait_replacements

class BoardAddition(object):
    """
    Describes a Player action to add a species board to their list to the
    right? of their list.
    """

    def __init__(self, payment_index, traits=None):
        """
        Constructs a player BoardAddition where the card in the player's hand
        at index payment_index is used to pay for the species and the indices for
        trait cards to be placed on the species are in te traits list.
        """
        self.payment_index = payment_index
        if not traits:
            self.traits = []
        else:
            self.traits = traits

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
