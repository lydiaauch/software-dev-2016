from player_state import *
from species import *
from feeding import *
from traitcard import TraitCard
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
        wh_cards: The face down cards whose food value will be added to the waterin' hole.
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
        self.wh_cards = []
        self.skipped_players = []


        for player, index in zip(player_interfaces, range(len(player_interfaces))):
            player_set = {'interface': player, 'state': PlayerState(index+1)}
            self.player_sets.append(player_set)

    def __eq__(self, other):
        """Compares two dealer objects"""
        return all([isinstance(other, Dealer),
                    # TODO: Implement equality for player sets.
                    len(self.player_sets) == len(other.player_sets),
                    self.deck == other.deck,
                    self.watering_hole == other.watering_hole,
                    self.current_player_index == other.current_player_index,
                    self.wh_cards == other.wh_cards])

    def run(self):
        """
        Runs a complete instance of the Evolution game.
        """
        self.create_deck()
        while len(self.deck) > self.min_deck_size():
            self.make_initial_species()
            self.deal_round()
            actions = self.get_player_actions()
            self.step4(actions)
            self.reduce_species_pop()
            self.move_food()
        self.move_food()

    def print_results(self):
        """
        Prints player ID's and scores in descending order.
        """
        results = ""
        sorted_players = self.player_states()
        sorted_players.sort(cmp=lambda p1, p2: p2.food_bag - p1.food_bag)
        for player, index in zip(sorted_players, range(len(sorted_players))):
            results += "%d player id: %d score: %d\n" % (index+1, player.name, player.food_bag)
        return results

    def create_deck(self):
        """
        Creates a deck of TraitCards.
        """
        for trait in TraitCard.traits:
            if trait == "carnivore":
                self.deck.extend(self.gen_cards(17, "carnivore"))
            else:
                self.deck.extend(self.gen_cards(7, trait))
        self.deck.sort(Dealer.compare_cards)

    def gen_cards(self, num_cards, trait_name):
        """
        Generates num_cards trait cards with the given trait_name and food points.
        If the card generated is a carnivore, the range of food_points is (-8,8),
        else the range of food_points is (-3, 3).
        """
        cards = []
        cards.append(TraitCard(trait_name, 0))
        for num in range(num_cards/2):
            cards.append(TraitCard(trait_name, num+1))
            cards.append(TraitCard(trait_name, -1*(num+1)))
        return cards

    @classmethod
    def compare_cards(cls, c1, c2):
        """
        Compares two trait cards. Returns -1 if c1 is less than c2, or 1 if
        c1 is larger than c2.
        """
        if c1.trait == c2.trait:
            if c1.food_points < c2.food_points:
                return -1
            else:
                return 1
        else:
            if c1.trait < c2.trait:
                return -1
            else:
                return 1

    def make_initial_species(self):
        """
        Gives each player without a species board one new species with a
        population of one.
        """
        for player in self.player_states():
            if len(player.species) == 0:
                player.species.append(Species())

    def min_deck_size(self):
        """
        Determines the lowest amount of cards the deck can have while still
        being able to give each player the appropriate number of cards at the
        start of a round.
        :return: The number of cards required to deal at the start of a round.
        """
        num_species = 0
        for player in self.player_states():
            num_species += len(player.species)
        min_cards = (3 * len(self.player_sets)) + num_species
        return min_cards

    def deal_round(self):
        """
        Gives each player one card per species board it owns and three additional
        cards.
        """
        for player in self.player_states():
            num_cards = 3 + len(player.species)
            self.deal(num_cards, player)

    def get_player_actions(self):
        """
        Gets player actions for each player using the choose method.
        :return: List-of-Action, on for each player in the game.
        """
        pass

    def reduce_species_pop(self):
        """
        Reduces each players species population to its food amount at the end of
        a round.
        """
        for player in self.player_states():
            for species in player.species:
                to_kill = species.population - species.food
                for _ in range(to_kill):
                    self.kill(player, species)

    def move_food(self):
        """
        Moves all food tokens from each players species to their food_bags.
        """
        for player in self.player_states():
            for species in player.species:
                player.food_bag += species.food
                species.food = 0

    def step4(self, step4):
        """
        Applies the given list of Actions and feeds the players' species until
        they cannot feed anymore.
        :param step4: List-of Action where action i corresponds with the action
        of the i'th player.
        """
        self.reveal_cards(step4)
        self.trigger_auto_traits()

        for player, action in zip(self.player_states(), step4):
            player.apply_action(action)

        self.move_fat_food()

        while self.watering_hole > 0 and len(self.player_sets) != len(self.skipped_players):
            self.feed1()

    def reveal_cards(self, step4):
        """
        Adds all food points from cards allocated for food in the given step4 to
        the waterin' hole.
        """
        for action, player in zip(step4, self.player_states()):
            food_card = player.hand[action.food_card]
            self.watering_hole += food_card.food_points
            food_card.used = True

        self.watering_hole = max(self.watering_hole, 0)

    def trigger_auto_traits(self):
        """
        Automatically updates the population or body size of a species with the
        Fertile or Long Neck traits
        """
        for player in self.player_states():
            for species in player.species:
                if "fertile" in species.trait_names():
                    species.population += 1

        for player in self.player_states():
            for species in player.species:
                if "long-neck" in species.trait_names():
                    self.feed(player, species)

    def move_fat_food(self):
        """
        Moves fat-food to normal food
        """
        for player in self.player_states():
            for species in player.species:
                if "fat-tissue" in species.trait_names():
                    species.digest_fat()

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

        if self.current_player_index in self.skipped_players or not self.player_can_feed(current_player):
            self.skip_player(self.current_player_index)
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

        non_feedable_carnivores = [carnivore for carnivore in non_feedable_carnivores
             if  "fat-tissue" not in carnivore.trait_names() or
                 ("fat-tissue" in carnivore.trait_names() and
                  carnivore.fat_storage == carnivore.body)]

        return hungries > 0 and len(hungries) != len(non_feedable_carnivores)

    def feed(self, player, species):
        """
        Feeds the given species food tokens from the watering hole. Accounts for
        foraging food amounts as well as cooperation feeding.
        :param player: The player who owns the given species.
        :sparam species: The species to be fed.
        """
        before_eating = species.food

        self.give_food(species)
        if "foraging" in species.trait_names():
            self.give_food(species)

        tokens_eaten = species.food - before_eating
        for _ in range(tokens_eaten):
            self.cooperate(player, species)

    def cooperate(self, player, species):
        """
        Triggers cooperation for the given species if it has the cooperation trait.
        :param player: The owner of the species to cooperate.
        :param species: The species cooperating.
        """
        if self.watering_hole >= 1:
            species_index = player.species.index(species)
            right_neighbor = (False if species_index == len(player.species) - 1
                                    else player.species[species_index + 1])
            if "cooperation" in species.trait_names() and right_neighbor:
                self.feed(player, right_neighbor)

    def give_food(self, species):
        """
        Gives the given species one food token from the watering hole if possible.
        :param species: The Species to be fed.
        """
        if species.population - species.food >= 1 and self.watering_hole >= 1:
            species.food += 1
            self.watering_hole -= 1

    def skip_player(self, player_index):
        """
        Removes the player at the given index from the player feeding order.
        :param player_index: The index of the player to remove in the player_sets
        array.
        """
        if player_index not in self.skipped_players:
            self.skipped_players.append(player_index)

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
            return self.herbivore_autoeat(eater, cur_player_species)

        if len(hungry_carnivores) == 1 and len(hungry_herbivores) == 0:
            eater = hungry_carnivores[0]
            return self.carnivore_autoeat(eater, cur_player_species)
        return None

    def herbivore_autoeat(self, eater, cur_player_species):
        """
        Constructs a Feeding for the given eater.
        :param eater: The herbivore species to feed.
        :param cur_player_species: List of the current player's species.
        eater must be an element of this list.
        """
        herbivore_index = cur_player_species.index(eater)
        if "fat-tissue" in eater.trait_names() and eater.fat_storage < eater.body:
            max_food = eater.body - eater.fat_storage
            food_requested = min(self.watering_hole, max_food)
            return FatTissueFeeding(herbivore_index, food_requested)
        else:
            return HerbivoreFeeding(herbivore_index)

    def carnivore_autoeat(self, eater, cur_player_species):
        """
        Constructs a Feeding for the given eater.
        :param eater: The carnivore species to feed.
        :param cur_player_species: List of the current player's species.
        eater must be an element of this list.
        """
        carnivore_index = cur_player_species.index(eater)
        targets = Dealer.carnivore_targets(eater, self.opponents())

        if len(targets) == 1:
            target_player = next(player for player in self.player_states()
                                if targets[0] in player.species)
            defender_index = target_player.species.index(targets[0])
            target_index = self.opponents().index(target_player)
            return CarnivoreFeeding(carnivore_index, target_index, defender_index)

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
        for i in range(min(num_cards, len(self.deck))):
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
