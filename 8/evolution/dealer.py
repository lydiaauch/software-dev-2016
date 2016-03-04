from player_state import *
from species import *

"""
A Dealer Object
"""

class Dealer(object):

    def __init__(self, list_of_player_interfaces):
        """
        create a Dealer object
        :param list_of_player_interfaces: list of player interfaces
        :param list_of_player_sets: dict of player interfaces and
        player states -> all player states are set to default
        :param deck: deck of TraitCards
        :param watering_hole: integer of food tokens
        :param current_player_index: index of current players turn
        """
        self.list_of_player_interfaces = list_of_player_interfaces
        self.list_of_player_sets = []
        self.deck = []
        self.watering_hole = 0
        self.current_player_index = 0

        for player in list_of_player_interfaces:
            player_set = {'interface': player, 'state': PlayerState()}
            self.list_of_player_sets.append(player_set)

    def feed1(self):
        """
        executes one step in the feeding cycle and updates the game state accordingly
        """
        current_player = self.list_of_player_sets[self.current_player_index]
        if self.watering_hole < 0:
            raise Exception("There is no food in the watering hole")
        self.next_feed(current_player)
        # process stuff here
        # TODO: Scavenge trait

    def next_feed(self, current_player):
        """
        gets the next species to feed
        :param current_player: the player which is choosing a species to feed
        :return: a Feeding
        """
        auto_eat = self.auto_eat(current_player['state'].species)
        if auto_eat:
            return auto_eat
        else:
            current_player['interface'].next_feeding(current_player['interface'], self.watering_hole, self.opponents())


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

    def auto_eat(self):
        """
        feeds a species when there is only one herbivore or one carnivore with one defender
        :param list_of_species: the current players species
        :return: A Feeding, or None if a feeding choice cannot be automatic.
        """
        current_player = self.list_of_player_sets[self.current_player_index]
        hungry_herbivores = [species for species in current_player['state'].species
                                if "carnivore" not in species.trait_names() and species.can_eat()]
        hungry_carnivores = [species for species in current_player['state'].species
                                if "carnivore" in species.trait_names() and species.can_eat()]
        if len(hungry_herbivores) == 1 and len(hungry_carnivores) == 0:
            if "fat-tissue" in hungry_herbivores[0].trait_names():
                max_food = hungry_herbivores[0].body - hungry_herbivores[0].fat_storage
                food_requested = min(self.watering_hole, max_food)
                return [hungry_herbivores[0], food_requested]
            else:
                return hungry_herbivores[0]
        if len(hungry_carnivores) == 1 and len(hungry_herbivores) == 0:
            # TODO: targets includes yourself
            targets = Dealer.carnivore_targets(hungry_carnivores[0],
                                               self.make_list_of_player_states())
            target_player = next(player for player in self.make_list_of_player_states() if targets[0] in player.species)
            if len(targets) == 1 and target_player != current_player['state']:
                return [hungry_carnivores[0], target_player, targets[0]]
        return None

    def make_list_of_player_states(self):
        """
        Gets the 'state' objects of all the players in the game's player dictionary.
        :return: A List of the player_state objects.
        """
        states = []
        for i in range(0, len(self.list_of_player_sets)):
            states.append(self.list_of_player_sets[i]['state'])
        return states

    def opponents(self):
        """
        get the player states of all non-current player
        :return: a list of player states
        """
        opponents = self.make_list_of_player_states()
        opponents.pop(self.current_player_index)
        return opponents

    #TODO Is this really what we want?
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
