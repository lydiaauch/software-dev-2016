from helpers import *
from player_state import PlayerState
from species import Species
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
        players: List of each players' PlayerState
        deck: List of TraitCards representing the game's deck. Where the beginning
            of the list is the top of the deck, and the end of the list is the bottom.
        watering_hole: Integer representing the board's number of available food tokens.
        current_player_index: Index of player_sets for the player whose turn it is.
        skipped_players: List of players who are no longer feeding in the current round.
    """

    def __init__(self, player_interfaces):
        """
        create a Dealer object
        :param player_interfaces: list of player interface
        """
        self.players = []
        self.deck = []
        self.watering_hole = 0
        self.current_player_index = 0
        self.skipped_players = []

        for index, player in enumerate(player_interfaces):
            self.players.append(PlayerState(player, index + 1))

    def __eq__(self, other):
        """Compares two dealer objects"""
        return all([isinstance(other, Dealer),
                    len(self.players) == len(other.players),
                    self.deck == other.deck,
                    self.watering_hole == other.watering_hole,
                    self.current_player_index == other.current_player_index,
                    self.wh_cards == other.wh_cards])

    def run(self):
        """
        Runs a complete instance of the Evolution game.
        """
        self.create_deck()
        while len(self.deck) > self.min_deck_size() and self.players:
            self.skipped_players = []
            self.make_initial_species()
            self.deal_round()
            self.players_start()
            actions = self.get_player_actions()
            self.validate_actions(actions)
            self.apply_actions(actions)
            self.reduce_species_pop()
            self.move_food()
        self.move_food()

    def create_deck(self):
        """
        Creates a deck of TraitCards.
        Creates 7 cards of each Trait with a value of [-3,3] except for carnivore
        where there are 17 cards created with a value of [-8,8].
        """
        for trait in TraitCard.traits:
            num_cards = 7
            if trait == "carnivore":
                num_cards = 17
            self.deck.extend(TraitCard.gen_cards(num_cards, trait))
        self.deck.sort(TraitCard.compare)

    def make_initial_species(self):
        """
        Gives each player without a species board one new species with a
        population of one.
        """
        for player in self.players:
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
        for player in self.players:
            num_species += len(player.species)
        min_cards = (3 * len(self.players)) + num_species
        return min_cards

    def deal_round(self):
        """
        Gives each player one card per species board it owns and three additional
        cards.
        """
        for player in self.players:
            num_cards = 3 + len(player.species)
            self.deal(num_cards, player)

    def players_start(self):
        """
        Calls start on each player with the current amount of food in the WH.
        """
        for player in self.players:
            player.start(self.watering_hole)

    def get_player_actions(self):
        """
        Gets player actions for each player using the choose method.
        :return: List-of-Action, for each player in the game.
        """
        actions = []
        before = []
        to_remove = []
        after = map(lambda plr: plr.species, self.players)
        for player in self.players:
            after = after[1:]
            choice = player.choose(before, after)
            if choice:
                actions.append(choice)
            else:
                to_remove.append(player)
            before.append(player.species)
        for player in to_remove:
            self.remove_player(player)
        return actions

    def validate_actions(self, actions):
        """
        Ensures that the list of actions contains valid actions for each player
        in the game. Removes any players whose actions are not valid.
        Effect: removes players from the self.players whose actions are invalid.
        :param actions: The list of Actions containing the requested Action of
        each player.
        """
        to_remove = []
        for i in range(len(self.players)):
            if not self.players[i].is_valid_action(actions[i]):
                to_remove.append(i)
        for i in to_remove:
            self.remove_player(self.players[i])
            remaining_actions = []
            for index, action in enumerate(actions):
                if index not in to_remove:
                    remaining_actions.append(action)

    def remove_player(self, player):
        """
        Removes the given player from the game permenantly.
        :param player: the player to remove from the game.
        """
        self.players.remove(player)
        if self.current_player_index == len(self.players):
            self.current_player_index = 0

    def reduce_species_pop(self):
        """
        Reduces each players species population to its food amount at the end of
        a round.
        """
        for player in self.players:
            for species in player.species:
                to_kill = species.population - species.food
                for _ in range(to_kill):
                    self.kill(player, species)

    def move_food(self):
        """
        Moves all food tokens from each players species to their food_bags.
        """
        for player in self.players:
            player.move_food_to_bag()

    def apply_actions(self, actions):
        """
        Applies the given list of Actions and feeds the players' species until
        they cannot feed anymore.
        :param actions: List-of Action where action i corresponds with the action
        of the i'th player.
        """
        self.reveal_cards(actions)
        self.trigger_auto_traits()

        for player, action in zip(self.players, actions):
            player.apply_action(action)

        self.move_fat_food()
        while self.watering_hole > 0 and len(self.players) != len(self.skipped_players):
            self.feed1()

    def reveal_cards(self, actions):
        """
        Adds all food points from cards allocated for food in the given actions to
        the waterin' hole.
        :param actions: List of Actions to get the food card selections from.
        """
        for action, player in zip(actions, self.players):
            food_card = player.hand[action.food_card]
            self.watering_hole += food_card.food_points
            food_card.used = True

        self.watering_hole = max(self.watering_hole, 0)

    def trigger_auto_traits(self):
        """
        Automatically updates the population or body size of a species with the
        Fertile or Long Neck traits
        """
        for player in self.players:
            player.trigger_fertile()
        for player in self.players:
            self.watering_hole = player.trigger_long_neck(self.watering_hole)

    def move_fat_food(self):
        """
        Moves fat-food to normal food
        """
        for player in self.players:
            player.trigger_fat_food()

    def feed1(self):
        """
        Executes one step in the feeding cycle and updates the game state accordingly
        Effect: Feeds one species of the current player, potentially triggerring
        other feedings.
        """
        current_player = self.players[self.current_player_index]
        if self.watering_hole <= 0:
            return

        if self.current_player_index in self.skipped_players or \
                not current_player.can_feed(self.opponents()):
            self.skip_cur_player()
            self.rotate_players()
            return

        feeding = self.next_feed()

        if feeding and self.validate_feeding(feeding):
            feeding.apply(self)
            self.rotate_players()
        else:
            self.remove_player(current_player)

    def validate_feeding(self, feeding):
        """
        Ensures that the given Feeding is valid to apply to the current player.
        :param feeding: The Feeding to validate.
        :return: True if it is a valid Feeding, else False.
        """
        return feeding.validate(self)

    def rotate_players(self):
        """
        Increments this dealer's current player index to the next player in the ordering.
        """
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def kill(self, player, species):
        """
        Removes one population token from the given species. If that species
        goes extinct 2 cards are dealt to the player.
        :param player: The player whose species is being killed.
        :param species: The species who is being killed.
        """
        extinct = player.kill(species)
        if extinct:
            self.deal(2, player)

    def skip_cur_player(self):
        """
        Removes the current player from the player feeding order.
        """
        if self.current_player_index not in self.skipped_players:
            self.skipped_players.append(self.current_player_index)

    def next_feed(self):
        """
        Gets the next species to feed for the current player.
        :return: a Feeding, either decided automatically if only one choice
        is present, or by asking the current player
        """
        auto_eat = self.auto_eat()
        if auto_eat is None:
            current_player = self.players[self.current_player_index]
            opponents = map(lambda plr: plr.public_state(), self.opponents())
            next_feeding = current_player.next_feeding(self.watering_hole, opponents)
            if next_feeding:
                return next_feeding
            else:
                self.remove_player(current_player)
                return False
        else:
            return auto_eat

    def auto_eat(self):
        """
        Feeds a species when there is only one herbivore or one carnivore with
        one attackable species.
        :return: A Feeding, or None if a feeding choice cannot be automatic.
        """
        cur_player_species = self.players[self.current_player_index].species

        hungry_herbivores = [species for species in cur_player_species
                             if "carnivore" not in species.traits and species.can_eat()]
        hungry_carnivores = [species for species in cur_player_species
                             if "carnivore" in species.traits and species.can_eat()]

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
        if "fat-tissue" in eater.traits and eater.fat_storage < eater.body:
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
        targets = carnivore_targets(eater, self.opponents())

        if len(targets) == 1:
            target_player = next(player for player in self.players
                                 if targets[0] in player.species)
            defender_index = target_player.species.index(targets[0])
            target_index = self.opponents().index(target_player)
            return CarnivoreFeeding(carnivore_index, target_index, defender_index)

    def feed_scavengers(self):
        """
        Gives one food token to all species with the scavenger trait.
        """
        for player in self.players:
            self.watering_hole = player.trigger_scavenging(self.watering_hole)

    def feed(self, player, species):
        """
        Updates the watering hole after a players feeding has been applied.
        :param player: The player currently feeding.
        :param species: The species the player is feeding.
        """
        self.watering_hole = player.feed(species, self.watering_hole)

    def deal(self, num_cards, player):
        """
        Gives num_cards to the player from the deck.
        :param num_cards: The number of cards to deal to the player.
        :param player: The player receiving the cards.
        """
        to_deal = min(num_cards, len(self.deck))
        for i in range(to_deal):
            card = self.deck.pop(0)
            player.hand.append(card)

    def check_for_hungries(self, list_of_species):
        """
        Finds the hungry species in a players list of species
        :param list_of_species: The players list of species.
        :return: List of hungry species.
        """
        hungries = []
        for species in list_of_species:
            if species.can_eat():
                hungries.append(species)
        return hungries

    def opponents(self):
        """
        get the player states of all non-current player
        :return: a list of player states
        """
        opponents = [plr for plr in self.players]
        opponents.pop(self.current_player_index)
        return opponents

    def get_scores(self):
        """
        Creates a List of Lists of player id to the associated player's score.
        Score is calculated by the sum of the food in the food bag, the sum of the
        population of each of that player's species, and the sum of the number
        of trait cards on each of their species.
        :return: A dictionary [[id, score], ...] for each player left in the game.
        """
        scores = []
        for player in self.players:
            score = player.food_bag
            for species in player.species:
                score += species.population
                score += len(species.traits)
            scores.append([player.name, score])
        return scores
