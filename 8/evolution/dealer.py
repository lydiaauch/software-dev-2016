from player_state import *
from species import *

"""
A Dealer Object.

A Feeding is one of:
- false if the player chooses not to feed.
- Natural if the herbivore at the given index is being fed.
- [Natural, Nat+] if a fat-tissue species at the given index is being
fed the Nat+ amount of food.
- [Natural, Natural, Natural] if the carnivore at the first index is
attacking the player at the second index, and defender species at the
third index. For the player index, the indices from 0 to num_players-2
represent the player's opponents, while the index num_players-1 is reserved
for the current player.

A Natural is a Natural number >= 0
A Nat+ is a Natural number > 0
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

    def feed1(self):
        """
        Executes one step in the feeding cycle and updates the game state accordingly
        :return: False if the current player cannot feed.
        True if the player is auto fed or makes a feeding decision
        :raises: Raises an exception if the watering hole starts at 0.
        """
        current_player = self.player_sets[self.current_player_index]['state']
        if not self.player_can_feed(current_player):
            self.current_player_index = (self.current_player_index + 1) % len(self.player_sets)
            return False

        if self.watering_hole <= 0:
            raise Exception("There is no food in the watering hole")
        feeding = self.next_feed()
        #TODO validate given feeding
        if feeding is not False:
            if isinstance(feeding, int):
                species = current_player.species[feeding]
                self.feed(current_player, species)
            elif len(feeding) == 2:
                food_requested = feeding[1]
                species = current_player.species[feeding[0]]
                if food_requested > self.watering_hole:
                    raise Exception("Fat tissue species asked for too much food.")
                self.watering_hole -= food_requested
                species.fat_storage += food_requested
            elif len(feeding) == 3:
                attacker = current_player.species[feeding[0]]
                if feeding[1] == len(self.player_sets) - 1:
                    target_player = current_player
                else:
                    target_player = self.opponents()[feeding[1]]
                defender = target_player.species[feeding[2]]
                if "horns" in defender.trait_names():
                    self.kill(current_player, attacker)
                self.feed(current_player, attacker)
                self.kill(target_player, defender)
                self.feed_scavengers()
        self.current_player_index = (self.current_player_index + 1) % len(self.player_sets)
        return True

    def kill(self, player, species):
        """
        Removes one population token from the given species. If that species
        goes extinct 2 cards are dealt to the player.
        :param player: The player whose species is being killed.
        :param species: The species who is being killed.
        """
        species.population -= 1
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
        if ("foraging" in species.trait_names() and
                species.population - species.food >= 2 and
                self.watering_hole >= 2):
            species.food += 2
            self.watering_hole -= 2
        elif (species.population - species.food >= 1 and
                self.watering_hole >= 1):
            species.food += 1
            self.watering_hole -= 1

        species_index = player.species.index(species)
        right_neighbor = (False if species_index == len(player.species) - 1
                                else player.species[species_index + 1])
        if "cooperation" in species.trait_names() and right_neighbor:
            self.feed(player, right_neighbor)

    def next_feed(self):
        """
        gets the next species to feed for the current player.
        :return: a Feeding, either decided automatically if only one obvious choice
        is present, or by asking the interface of the current player
        """
        auto_eat = self.auto_eat()
        current_player = self.player_sets[self.current_player_index]
        if auto_eat is None:
            cur_player = current_player['state'].public_state()
            opponents  = map(lambda spec: spec.public_state(), self.opponents())
            return current_player['interface'].next_feeding(cur_player, self.watering_hole, opponents)
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
                return [herbivore_index, food_requested]
            else:
                return herbivore_index

        if len(hungry_carnivores) == 1 and len(hungry_herbivores) == 0:
            eater = hungry_carnivores[0]
            carnivore_index = cur_player_species.index(eater)
            targets = Dealer.carnivore_targets(eater, self.opponents())
            target_player = next(player for player in self.player_states()
                                    if targets[0] in player.species)

            if len(targets) == 1 and target_player.species != cur_player_species:
                defender_index = target_player.species.index(targets[0])
                target_index = self.opponents().index(target_player)
                return [carnivore_index, target_index, defender_index]
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
