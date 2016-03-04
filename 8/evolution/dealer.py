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
        if self.watering_hole <= 0:
            raise Exception("There is no food in the watering hole")
        feeding = self.next_feed(current_player)
        #TODO validate given feeding
        if feeding is not False:
            if isinstance(feeding, int):
                species = current_player['state'].species[feeding]
                self.watering_hole -= 1
                species.food += 1
            elif len(feeding) == 2:
                food_requested = feeding[1]
                species = current_player['state'].species[feeding[0]]
                if food_requested > self.watering_hole:
                    raise Exception("Fat tissue species asked for too much food.")
                self.watering_hole -= food_requested
                species.fat_storage += food_requested
            elif len(feeding) == 3:
                attacker = current_player['state'].species[feeding[0]]
                target_player = self.list_of_player_sets[feeding[1]]['state']
                defender = target_player.species[feeding[2]]
                defender.population -= 1
                attacker.food += 1
                self.watering_hole -= 1
                self.feed_scavengers()
                if defender.population == 0:
                    target_player.species.remove(defender)
                    self.deal(2, target_player)

        self.current_player_index = (self.current_player_index + 1) % len(self.list_of_player_sets)

    def next_feed(self, current_player):
        """
        gets the next species to feed
        :param current_player: the player which is choosing a species to feed
        :return: a Feeding
        """
        auto_eat = self.auto_eat()
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
        current_player = self.list_of_player_sets[self.current_player_index]
        hungry_herbivores = [species for species in current_player['state'].species
                                if "carnivore" not in species.trait_names() and species.can_eat()]
        hungry_carnivores = [species for species in current_player['state'].species
                                if "carnivore" in species.trait_names() and species.can_eat()]
        if len(hungry_herbivores) == 1 and len(hungry_carnivores) == 0:
            herbivore_index = current_player['state'].species.index(hungry_herbivores[0])
            if "fat-tissue" in hungry_herbivores[0].trait_names():
                max_food = hungry_herbivores[0].body - hungry_herbivores[0].fat_storage
                food_requested = min(self.watering_hole, max_food)
                return [herbivore_index, food_requested]
            else:
                return herbivore_index
        if len(hungry_carnivores) == 1 and len(hungry_herbivores) == 0:
            carnivore_index = current_player['state'].species.index(hungry_carnivores[0])
            targets = Dealer.carnivore_targets(hungry_carnivores[0],
                                               self.opponents())
            target_player = next(player for player in self.make_list_of_player_states() if targets[0] in player.species)
            if len(targets) == 1 and target_player != current_player['state']:
                defender_index = target_player.species.index(targets[0])
                target_index = self.make_list_of_player_states().index(target_player);
                return [carnivore_index, target_index, defender_index]
        return None

    def feed_scavengers(self):
        """
        Gives one food token to all species with the scavenger trait.
        """
        for player in self.make_list_of_player_states():
            for species in player.species:
                if "scavenger" in species.trait_names() and species.food < species.population:
                    species.food += 1
                    self.watering_hole -= 1

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
