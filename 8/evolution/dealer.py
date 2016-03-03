from player_state import *

"""
A Dealer Object
"""

class Dealer(object):

    def __init__(self, list_of_player_interfaces):
        """
        create a Dealer object
        :param list_of_player_interfaces: list of player interfaces
        :param list_of_player_sets: dict of player interfaces and player states -> all player states are set to default
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


    def auto_eat(self, list_of_species):
        """
        feeds a species when there is only one herbivore or one carnivore with one defender
        :param list_of_species: the current players species
        :return: species to feed
        """
        pass

    def opponents(self):
        """
        get the player states of all non-current player
        :return: a list of player states
        """
        pass






