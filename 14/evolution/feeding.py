class AbstainFeeding(object):
    def apply(self, dealer):
        """
        Applies the consequences of this feeding to the given dealer.
        :param dealer: The game this Feeding effects.
        """
        dealer.skip_cur_player()

    def __eq__(self, other):
        return isinstance(other, AbstainFeeding)

    def validate(self, dealer):
        """
        Ensures that this Feeding is valid to apply to the given Dealer.
        :param dealer: The Dealer whose feeding is being validated.
        :return: True if it is a valid Feeding, else False.
        """
        return True


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

    def __eq__(self, other):
        return isinstance(other, HerbivoreFeeding) and self.species_index == other.species_index

    def validate(self, dealer):
        """
        Ensures that this Feeding is valid to apply to the given Dealer.
        :param dealer: The Dealer whose feeding is being validated.
        :return: True if it is a valid Feeding, else False.
        """
        player = dealer.players[dealer.current_player_index]
        if len(player.species) > self.species_index:
            spec = player.species[self.species_index]
            return spec.population > spec.food
        else:
            return False


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

    def __eq__(self, other):
        return isinstance(other, FatTissueFeeding) and \
            all([self.species_index == other.species_index,
                 self.food_requested == other.food_requested])

    def validate(self, dealer):
        """
        Ensures that this Feeding is valid to apply to the given Dealer.
        :param dealer: The Dealer whose feeding is being validated.
        :return: True if it is a valid Feeding, else False.
        """
        player = dealer.players[dealer.current_player_index]
        if len(player.species) > self.species_index:
            spec = player.species[self.species_index]
            return spec.body >= (spec.fat_storage + self.food_requested) and \
                "fat-tissue" in spec.traits
        else:
            return False


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

    def __str__(self):
        return "attacker: %d, target player: %d, defender: %d" % (self.attacker_index, self.target_index, self.defender_index)

    def __eq__(self, other):
        return isinstance(other, CarnivoreFeeding) and \
            all([self.attacker_index == other.attacker_index,
                 self.target_index == other.target_index,
                 self.defender_index == other.defender_index])

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

    def validate(self, dealer):
        """
        Ensures that this Feeding is valid to apply to the given Dealer.
        :param dealer: The Dealer whose feeding is being validated.
        :return: True if it is a valid Feeding, else False.
        """
        if self.target_index < len(dealer.players):
            attacking_player = dealer.players[dealer.current_player_index]
            defending_player = dealer.opponents()[self.target_index]
            if len(attacking_player.species) > self.attacker_index and \
                    len(defending_player.species) > self.defender_index:
                attacker = attacking_player.species[self.attacker_index]
                defender = defending_player.species[self.defender_index]
                left = (False if self.defender_index == 0
                             else defending_player.species[self.defender_index - 1])
                right = (False if self.defender_index == len(defending_player.species) - 1
                              else defending_player.species[self.defender_index + 1])
                return defender.is_attackable(attacker, left, right)
            else:
                return False
        else:
            return False
