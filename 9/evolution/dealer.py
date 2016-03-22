from player_state import *
from species import *
from feeding import *
"""
A Dealer Object.
"""

class Dealer(object):
    """
    A representation of a game of Evolution containing both the state of the game,
    and the API to progress though it.

    Attributes:
        player_sets: List of Dicts for each player's 'interface' and 'state'.
            Ex. self.player_sets[self.current_player_index]['state'] would get
            the state of the current player.
        deck: List of TraitCards representing the game's deck. Where the beginning
            of the list is the top of the deck, and the end of the list is the bottom.
        watering_hole: Integer representing the board's number of available food tokens.
        current_player_index: Index of player_sets for the player whose turn it is.
    """

    def __init__(self, player_interfaces):
        """
        create a Dealer object
        :param player_interfaces: list of player interfaces
        """
        self.player_sets = []
        self.deck = []
        self.watering_hole = 0
        self.current_player_index = 0

        for player in player_interfaces:
            player_set = {'interface': player, 'state': PlayerState()}
            self.player_sets.append(player_set)

    def __eq__(self, other):
        """Compares two dealer objects"""
        return all([isinstance(other, Dealer),
                    # TODO: Implement equality for player sets.
                    len(self.player_sets) == len(other.player_sets),
                    self.deck == other.deck,
                    self.watering_hole == other.watering_hole,
                    self.current_player_index == other.current_player_index])

    def feed1(self):
        """
        Executes one step in the feeding cycle and updates the game state accordingly
        :return: False if the current player cannot feed.
        True if the player is auto fed or makes a feeding decision
        :raises: Raises an exception if the watering hole starts at 0.
        """
        current_player = self.player_sets[self.current_player_index]['state']

        if self.watering_hole <= 0:
            return

        if not self.player_can_feed(current_player):
            self.current_player_index = (self.current_player_index + 1) % len(self.player_sets)
            return

        feeding = self.next_feed()
        #TODO validate given feeding
        feeding.apply(self)
        self.current_player_index = (self.current_player_index + 1) % len(self.player_sets)

    def kill(self, player, species):
        """
        Removes one population token from the given species. If that species
        goes extinct 2 cards are dealt to the player.
        :param player: The player whose species is being killed.
        :param species: The species who is being killed.
        """
        species.population -= 1
        species.food = min(species.food, species.population)

        if species.population == 0:
            player.species.remove(species)
            self.deal(2, player)

    def player_can_feed(self, player):
        """
        Checks if any of the given player's species can eat. Checks either for
        herbivore species who can eat from the watering hole, or carnivores
        which have valid targets.
        :param player: The player whose options are being checked for valid Feedings.
        :return: True if the player has at least one valid Feeding, otherwise false.
        """
        hungries = [species for species in player.species if species.can_eat()]
        non_feedable_carnivores = \
            [carnivore for carnivore in hungries if
                "carnivore" in carnivore.trait_names() and
                len(Dealer.carnivore_targets(carnivore, self.player_states())) == 0]

        return hungries > 0 and len(hungries) != len(non_feedable_carnivores)

    def feed(self, player, species):
        """
        Feeds the given species food tokens from the watering hole. Accounts for
        foraging food amounts as well as cooperation feeding.
        :param player: The player who owns the given species.
        :sparam species: The species to be fed.
        """
        has_fed = False
        if ("foraging" in species.trait_names() and
                species.population - species.food >= 2 and
                self.watering_hole >= 2):
            species.food += 2
            self.watering_hole -= 2
            has_fed = True
        elif (species.population - species.food >= 1 and
                self.watering_hole >= 1):
            species.food += 1
            self.watering_hole -= 1
            has_fed = True

        species_index = player.species.index(species)
        right_neighbor = (False if species_index == len(player.species) - 1
                                else player.species[species_index + 1])
        if "cooperation" in species.trait_names() and right_neighbor and has_fed:
            self.feed(player, right_neighbor)

    def remove_player(self, player_index):
        """
        Removes the player at the given index from the player feeding order.
        :param player_index: The index of the player to remove in the player_sets
        array.
        """
        # TODO Implement the player abstaining for future rounds.
        pass

    def next_feed(self):
        """
        gets the next species to feed for the current player.
        :return: a Feeding, either decided automatically if only one obvious choice
        is present, or by asking the interface of the current player
        """
        auto_eat = self.auto_eat()
        if auto_eat is None:
            current_player = self.player_sets[self.current_player_index]
            return current_player['interface'].next_feeding(current_player['state'],
                                    self.watering_hole, self.opponents())
        else:
            return auto_eat

    def auto_eat(self):
        """
        feeds a species when there is only one herbivore or one carnivore with one defender
        :param list_of_species: the current players species
        :return: A Feeding, or None if a feeding choice cannot be automatic.
        """
        cur_player_species = self.player_state(self.current_player_index).species

        hungry_herbivores = [species for species in cur_player_species
                                if "carnivore" not in species.trait_names() and species.can_eat()]
        hungry_carnivores = [species for species in cur_player_species
                                if "carnivore" in species.trait_names() and species.can_eat()]

        if len(hungry_herbivores) == 1 and len(hungry_carnivores) == 0:
            eater = hungry_herbivores[0]
            herbivore_index = cur_player_species.index(eater)

            if "fat-tissue" in eater.trait_names():
                max_food = eater.body - eater.fat_storage
                food_requested = min(self.watering_hole, max_food)
                return FatTissueFeeding(herbivore_index, food_requested)
            else:
                return HerbivoreFeeding(herbivore_index)

        if len(hungry_carnivores) == 1 and len(hungry_herbivores) == 0:
            eater = hungry_carnivores[0]
            carnivore_index = cur_player_species.index(eater)
            targets = Dealer.carnivore_targets(eater, self.opponents())

            if len(targets) == 1:
                target_player = next(player for player in self.player_states()
                                    if targets[0] in player.species)
                defender_index = target_player.species.index(targets[0])
                target_index = self.opponents().index(target_player)
                return CarnivoreFeeding(carnivore_index, target_index, defender_index)
        return None

    def feed_scavengers(self):
        """
        Gives one food token to all species with the scavenger trait.
        """
        for player in self.player_states():
            for species in player.species:
                if "scavenger" in species.trait_names() and species.food < species.population:
                    self.feed(player, species)

    def deal(self, num_cards, player):
        """
        Gives num_cards to the player from the deck.
        """
        for i in range(num_cards):
            card = self.deck.pop(0)
            player.hand.append(card)

    def check_for_hungries(self, list_of_species):
        """
        looks for hungry species in a players list of species
        :return: list of hungry species
        """
        hungries = []
        for species in list_of_species:
            if species.can_eat():
                hungries.append(species)
        return hungries

    def player_state(self, i):
        """
        Gets the state of the player at the ith index of the game's player list.
        :param: i The index of the player's state
        :return: A PlayerState object representing the ith player.
        """
        return self.player_sets[i]['state']

    def player_states(self):
        """
        Gets the 'state' objects of all the players in the game's player dictionary.
        :return: A List of the player_state objects.
        """
        states = []
        for i in range(0, len(self.player_sets)):
            states.append(self.player_sets[i]['state'])
        return states

    def opponents(self):
        """
        get the player states of all non-current player
        :return: a list of player states
        """
        opponents = self.player_states()
        opponents.pop(self.current_player_index)
        return opponents

    @classmethod
    def carnivore_targets(cls, carnivore, list_of_player):
        """
        Creates a list of all possible targets for given carnivore from the list of
        players.
        :param: carnivore The attacking carnivore.
        :param: list_of_player All players to be considered for possible targets.
        """
        targets = []
        for player in list_of_player:
            for i in range(0, len(player.species)):
                defender = player.species[i]
                left_neighbor = (False if i == 0 else player.species[i - 1])
                right_neighbor = (False if i == len(player.species) - 1 else player.species[i + 1])
                if defender.is_attackable(carnivore, left_neighbor, right_neighbor) and defender != carnivore:
                    targets.append(defender)
        return targets
