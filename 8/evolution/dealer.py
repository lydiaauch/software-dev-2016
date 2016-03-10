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
third index.

A Natural is a Natural number >= 0
A Nat+ is a Natural number > 0
"""

class Dealer(object):

    def __init__(self, player_interfaces):
        """
        create a Dealer object
        :param player_interfaces: list of player interfaces
        :param player_sets: dict of player interfaces and
        player states -> all player states are set to default
        :param deck: deck of TraitCards
        :param watering_hole: integer of food tokens
        :param current_player_index: index of current players turn
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
        # TODO: traits Foraging, Horns
        current_player = self.player_sets[self.current_player_index]['state']
        hungries = [species for species in current_player.species if species.can_eat()]
        if len(hungries) == 0:
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
                target_player = self.player_sets[feeding[1]]['state']
                defender = target_player.species[feeding[2]]
                defender.population -= 1
                if "horns" in defender.trait_names():
                    attacker.population -= 1
                self.feed(current_player, attacker)
                self.feed_scavengers()
                if defender.population == 0:
                    target_player.species.remove(defender)
                    self.deal(2, target_player)

        self.current_player_index = (self.current_player_index + 1) % len(self.player_sets)
        return True

    def feed(self, player, species):
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
        if right_neighbor:
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
                target_index = self.player_states().index(target_player);
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
        pass

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
                if defender.is_attackable(carnivore, left_neighbor, right_neighbor):
                    targets.append(defender)
        return targets
