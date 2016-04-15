class AbstainFeeding(object):
    def apply(self, dealer):
        """
        Applies the consequences of this feeding to the given dealer.
        :param dealer: The game this Feeding effects.
        """
        dealer.skip_cur_player()


class HerbivoreFeeding(object):
    def __init__(self, species_index):
        """
        Creates a new VegitarianFeeding given the index of the species to feed.
        :param species_index: The index of the species to feed in the player's
        list of species
        """
        self.species_index = species_index

    def apply(self, dealer):
        """
        Applies the consequences of this feeding to the given dealer.
        :param dealer: The game this Feeding effects.
        """
        current_player = dealer.players[dealer.current_player_index]
        species = current_player.species[self.species_index]
        dealer.feed(current_player, species)


class FatTissueFeeding(object):
    def __init__(self, species_index, food_requested):
        """
        Creates a new FatTissueFeeding given the index of the species to fill up
        and the amount of food they'd like to store.
        :param species_index: The index of the species to feed in the player's
        list of species.
        :param food_requested: The amound of food to place on the fat tissue card.
        """
        self.species_index = species_index
        self.food_requested = food_requested

    def apply(self, dealer):
        """
        Applies the consequences of this feeding to the given dealer.
        :param dealer: The game this Feeding effects.
        """
        species = dealer.players[dealer.current_player_index].species[self.species_index]
        dealer.watering_hole -= self.food_requested
        species.fat_storage += self.food_requested


class CarnivoreFeeding(object):
    def __init__(self, attacker_index, target_index, defender_index):
        """
        Creates a new CarnivoreFeeding given the index of the attacking species,
        the index of the player who owns the species to attack, and the index of
        the defending species.
        :param attacker_index: The index of the attacking species in the current
        player's list of species.
        :param target_index: The index of the player to target in the list of
        opponents with the current player at the end.
        :param defender_index: The index of the defending species in the target
        player's list of species.
        """
        self.attacker_index = attacker_index
        self.target_index = target_index
        self.defender_index = defender_index

    def apply(self, dealer):
        """
        Applies the consequences of this feeding to the given dealer.
        :param dealer: The game this Feeding effects.
        """
        current_player = dealer.players[dealer.current_player_index]
        attacker = current_player.species[self.attacker_index]
        if self.target_index == len(dealer.players) - 1:
            target_player = current_player
        else:
            target_player = dealer.opponents()[self.target_index]
        defender = target_player.species[self.defender_index]
        dealer.kill(target_player, defender)
        if "horns" in defender.traits:
            dealer.kill(current_player, attacker)
        if attacker.population != 0:
            dealer.feed(current_player, attacker)
            dealer.feed_scavengers()
