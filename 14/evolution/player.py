from actions import *
from feeding import *
from traitcard import TraitCard
from helpers import *
from globals import *


class Player(object):
    """
    A data representation of a Player in the Evolution game
    """
    def __init__(self):
        self.player_state = None

    def start(self, player_state, wh):
        """
        Gives the player its state at the beginning of a round. This would allow
        a stateful player to begin to compute possible moves, but since this
        player is not stateful this method does nothing.
        :param player_state: The PlayerState representing this player.
        """
        self.player_state = player_state
        self.watering_hole = wh

    def choose(self, choice):
        """
        Returns the players Action representing how this player wants to use their
        cards for the current round.
        :param choice: A Choice object representing the state of the species before
        and after the current player.
        :return: An Action representing how the player is using their cards for
        the round.
        """
        cards = []
        for i, card in enumerate(self.player_state.hand):
            cards.append({"card": card, "index": i})
        cards.sort(lambda c0, c1: TraitCard.compare(c0['card'], c1['card']))

        food_card = cards[0]['index']
        action = Action(food_card, [], [], [], [])
        action.species_additions.append(BoardAddition(cards[1]['index'],
                                                      [cards[2]['index']]))
        if len(self.player_state.hand) > 3:
            action.pop_grows.append(PopGrow(len(self.player_state.species), cards[3]['index']))
        if len(self.player_state.hand) > 4:
            action.body_grows.append(BodyGrow(len(self.player_state.species), cards[4]['index']))
        if len(self.player_state.hand) > 5:
            action.trait_replacements.append(ReplaceTrait(len(self.player_state.species),
                                                          0,
                                                          cards[5]['index']))
        return action

    def next_feeding(self, player, food_available, opponents):
        """
        Determines a players next feeding species
        :param player: the PlayerState of the player who is feeding
        :param food_available: the amount of food on the watering hole board
        :param opponents: the PlayerStates of other players in the game
        :return: feeding action for the next species to feed
        """
        hungry_fatties = [species for species in player.species
                          if "fat-tissue" in species.traits and
                          species.fat_storage < species.body]
        if hungry_fatties:
            feeding = Player.feed_fatty(hungry_fatties, food_available)
            return FatTissueFeeding(player.species.index(feeding[0]), feeding[1])

        hungry_species = [species for species in player.species if species.can_eat()]
        hungry_carnivores = [species for species in hungry_species
                             if "carnivore" in species.traits]

        hungry_herbivores = Player.find_hungry_herbs(hungry_species, hungry_carnivores)
        if hungry_herbivores:
            feeding = Player.feed_herbivores(hungry_herbivores)
            return HerbivoreFeeding(player.species.index(feeding))
        if hungry_carnivores:
            feeding = Player.feed_carnivore(hungry_carnivores, player, opponents)
            if feeding:
                return Player.species_to_index(feeding, player, opponents)
        return AbstainFeeding()

    @classmethod
    def species_to_index(cls, feeding, player, opponents):
        """
        Converts the given feeding to a feeding with indices
        :param feeding: the chosen feeding.
        :param player: the PlayerState of the player who is feeding
        :param opponents: the PlayerStates of other players in the game
        """
        attacking_species_index = player.species.index(feeding[0])
        defending_player_index = opponents.index(feeding[1])
        defending_species_index = feeding[1].species.index(feeding[2])
        return CarnivoreFeeding(attacking_species_index,
                                defending_player_index,
                                defending_species_index)

    @classmethod
    def find_hungry_herbs(cls, hungry_species, hungry_carnivores):
        """
        Creates a list of hungry herbivores from a list of hungry
        species and hungry carnivores
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
        Feeds a species with the fat-tissue trait
        :param fat_tissue_species: species with a fat-tissue trait
        :param food_available: food on the watering_hole_board
        :return: list of [Species, int] where Species is the
        fat_tissue_species and int is the requested food
        """
        fatty = cls.largest_fatty_need(fat_tissue_species)
        food_needed = fatty.body - fatty.fat_storage
        food_requested = (food_needed if food_needed < food_available else food_available)
        return [fatty, food_requested]

    @classmethod
    def feed_herbivores(cls, hungry_herbivores):
        """
        Feeds a herbivore species
        :param hungry_herbivores: list of hungry herbivores
        :return: the Species to feed
        """
        return cls.sort_lex(hungry_herbivores)[0]

    @classmethod
    def feed_carnivore(cls, hungry_carnivores, player, opponents):
        """
        Feeds the largest hungry carnivore
        :param hungry_carnivores: list of hungry carnivores
        :param player: the current player's state
        :param opponents: list of all other player's states
        :return: An array of [attacking_species, def_player, def_species] or
        False if not possible.
        """
        sorted_carnivores = cls.sort_lex(hungry_carnivores)
        for carnivore in sorted_carnivores:
            targets = carnivore_targets(carnivore, opponents)
            if targets:
                sorted_targets = cls.sort_lex(targets)
                target = sorted_targets[0]
                target_player = next(player for player in opponents if target in player.species)
                return [carnivore, target_player, target]

        return False

    @classmethod
    def largest_tied_species(cls, list_of_species):
        """
        Returns the largest tied species of a Player's species, in terms of lexicographical order
        :param list_of_species: a Player's species boards
        :return: list of largest Species
        """
        sorted_species = cls.sort_lex(list_of_species)
        largest = sorted_species[0]
        largest_species = [species for species in sorted_species
                           if species.population == largest.population and
                           species.food == largest.food and
                           species.body == largest.body]
        return largest_species

    @classmethod
    def sort_lex(cls, list_of_species):
        """
        Returns the largest species in a list based on a lexicographic manner
        :param list_of_species: a list of Species
        :return: the largest Species
        """
        return sorted(list_of_species, cmp=cls.is_larger, reverse=True)

    @classmethod
    def is_larger(cls, species_1, species_2):
        """
        Determines which of the two given species are larger based on a lexicographic manner
        :param species_1: first species to compare
        :param species_2: second species to compare
        :return: 1 if the first species is larger, -1 if the second is larger, 0 if they are equal
        """
        if species_1.population > species_2.population:
            return 1
        elif species_1.population == species_2.population:
            if species_1.food > species_2.food:
                return 1
            elif species_1.food == species_2.food:
                if species_1.body > species_2.body:
                    return 1
                elif species_1.body == species_2.body:
                    return 0
        return -1

    @classmethod
    def largest_fatty_need(cls, list_of_species):
        """
        Determines which species has a greater need for fat-tissue food
        :param list_of_species: list of Species with the fat-tissue trait
        :return: Species with greatest fat-tissue need
        """
        if len(list_of_species) == 1:
            return list_of_species[0]
        else:
            max_need = max([species.population - species.food for species in list_of_species])

        highest_needers = [species for species in list_of_species
                           if species.population - species.food == max_need]
        largest_needers = cls.largest_tied_species(highest_needers)
        if len(largest_needers) > 1:
            positions = [list_of_species.index(species) for species in largest_needers]
            return largest_needers[positions.index(min(positions))]
        else:
            return largest_needers[0]
