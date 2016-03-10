import os
import sys

from species import Species
from dealer import Dealer

globals_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "..%s" % os.sep)
sys.path.append(globals_path)

from globals import *


class Player(object):
    """
    A data representation of a Player in the Evolution game
    """
    def __init__(self):
        pass

    @classmethod
    def next_feeding(cls, player, food_available, list_of_players):
        """
        Determines a players next feeding species
        :param player: the PlayerState of the player who is feeding
        :param food_available: the amount of food on the watering hole board
        :param list_of_players: the PlayerStates of other players in the game
        :return: feeding action for the next species to feed
        """
        hungry_fatties = [species for species in player.species
                          if "fat-tissue" in species.trait_names()
                          and species.fat_storage < species.body]

        if hungry_fatties:
            # TODO: I'm confused. feed_fatty takes a single fatty species
            # but we're giving it list?
            feeding = cls.feed_fatty(hungry_fatties, food_available)
            return [player.species.index(feeding[0]), feeding[1]]

        # Checks sequencing constraints
        hungry_species = [species for species in player.species
                            if species.can_eat()]

        hungry_carnivores = [species for species in hungry_species
                                if "carnivore" in species.trait_names()]

        if(len(hungry_species) < MIN_HUNGRY_SPECIES
            and not any(hungry_carnivores)) or food_available <= 0:

            raise Exception("Must have food available, one hungry carnivore, \
                or two hungry herbivores to choose")

        hungry_herbivores = cls.find_hungry_herbs(hungry_species, hungry_carnivores)
        if hungry_herbivores:
            feeding = cls.feed_herbivores(hungry_herbivores)
            return player.species.index(feeding)

        if hungry_carnivores:
            feeding = cls.feed_carnivore(hungry_carnivores, player, list_of_players)
            if feeding:
                attacking_species_index = player.species.index(feeding[0])
                defending_player_index = list_of_players.index(feeding[1])
                defending_species_index = feeding[1].species.index(feeding[2])
                return [attacking_species_index,
                        defending_player_index,
                        defending_species_index]

        return False

    @classmethod
    def find_hungry_herbs(cls, hungry_species, hungry_carnivores):
        """
        Filters all carnivores from the hungry_carnivores list out of the
        given hungry_species list.
        :param hungry_species: list of hungry species
        :param hungry_carnivores: list of hungry carnivores
        :return: list of hungry herbivores
        """
        hungry_herbs = []
        for species in hungry_species:
            if species not in hungry_carnivores:
                hungry_herbs.append(species)
        return hungry_herbs

    @classmethod
    def feed_fatty(cls, fat_tissue_species, food_available):
        """
        Creates a Feeding for the given fat_tissue_species.
        :param fat_tissue_species: species with a fat-tissue trait to feed.
        :param food_available: food on the watering_hole_board
        :return: A Feeding [Species, int] where Species is the
        fat_tissue_species and int is the requested food
        """
        fatty = Species.largest_fatty_need(fat_tissue_species)
        food_needed = fatty.body - fatty.fat_storage
        food_requested = (food_needed if food_needed < food_available
                                      else food_available)
        return [fatty, food_requested]

    @classmethod
    def feed_herbivores(cls, hungry_herbivores):
        """
        Feeds a herbivore species
        :param hungry_herbivores: list of hungry herbivores
        :return: the Species to feed
        """
        return Species.sort_lex(hungry_herbivores)[0]

    @classmethod
    def feed_carnivore(cls, hungry_carnivores, player_state, list_of_player):
        """
        Feeds the largest hungry carnivore
        :param hungry_carnivores: list of hungry carnivores
        :param player_state: the current player state
        :param list_of_player: list of all player states
        :return:
        """
        sorted_carnivores = Species.sort_lex(hungry_carnivores)
        for carnivore in sorted_carnivores:
            targets = Dealer.carnivore_targets(carnivore, list_of_player)
            if targets:
                sorted_targets = Species.sort_lex(targets)
                target = sorted_targets[0]
                target_player = next(player for player in list_of_player
                                        if target in player.species)
                return [carnivore, target_player, target]

        return False
