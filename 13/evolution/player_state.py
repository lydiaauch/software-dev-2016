from species import Species
from actions import *
from choice import Choice


class PlayerState(object):
    """
    Represents data about the player that is kept track of by the dealer
    in order to prevent the player from modifying their data or acting out of turn
    the dealer only sends the minimum amount of data needed for the player to make
    choices

    Attributes:
        interface: A Class the player delegates strategy decisions to.
        name: An Integer identifier for the player.
        food_bag: Integer representing the number of food tokens acquired.
        hand: A List of `TraitCards` representing the cards the player can use.
        species: A List of `Species` representing the species boards the player
            has in front of them. Species are ordered from left to right.
    """
    def __init__(self, interface, name=None, food_bag=None, hand=None, species=None):
        if food_bag is None:
            food_bag = 0
        if hand is None:
            hand = []
        if species is None:
            species = []

        self.interface = interface
        self.name = name
        self.food_bag = food_bag
        self.hand = hand
        self.species = species

    def __str__(self):
        return "PlayerState(Food=%d, Hand=%s, Species=%s" % (self.food_bag, self.hand, self.species)

    def __eq__(self, other):
        return all([isinstance(other, PlayerState),
                    self.interface == other.interface,
                    self.name == other.name,
                    self.food_bag == other.food_bag,
                    self.hand == other.hand,
                    self.species == other.species])

    def apply_action(self, action):
        """
        Applies all parts of the given action to this player state.
        :param action: An Action to apply.
        """
        self.create_new_boards(action.species_additions)
        self.replace_traits(action.trait_replacements)
        self.increase_populations(action.pop_grows)
        self.increase_body_sizes(action.body_grows)
        self.remove_used_cards()

    def create_new_boards(self, board_additions):
        """
        Creates new Species for each BoardAddition in the given list of additions.
        :param board_additions: List of BoardAdditions to construct species from.
        """
        for addition in board_additions:
            self.hand[addition.payment_index].used = True
            traits = []
            for trait_idx in addition.traits:
                new_trait = self.hand[trait_idx]
                traits.append(new_trait.trait)
                new_trait.used = True
            self.species.append(Species(traits=traits))

    def replace_traits(self, trait_replacements):
        """
        Swaps out traits as described in the list of ReplaceTraits.
        :param trait_replacements: The list of ReplaceTrait to use.
        """
        for replace in trait_replacements:
            species = self.species[replace.species_index]
            new_trait = self.hand[replace.new_trait_index]
            species.replace_trait(replace.removed_trait_index, new_trait.trait)
            new_trait.used = True

    def increase_populations(self, pop_grows):
        """
        Increases the population by one for each speices described in the given
        list of PopGrow.
        :param pop_grows: List of PopGrow representing species whose population
        should be increased.
        """
        for grow in pop_grows:
            self.species[grow.species_index].breed()
            self.hand[grow.payment_index].used = True

    def increase_body_sizes(self, body_grows):
        """
        Increases the body size by one for each speices described in the given
        list of BodyGrow.
        :param body_grows: List of BodyGrow representing species whose body size
        should be increased.
        """
        for grow in body_grows:
            self.species[grow.species_index].grow_body()
            self.hand[grow.payment_index].used = True

    def remove_used_cards(self):
        """
        Removes all cards from this player's hand that are marked used.
        """
        self.hand = filter(lambda c: not c.used, self.hand)

    def public_state(self):
        """
        Creates a new player with private information set to defaults.
        :return: A new PlayerState object with the same information as this
        player state, but with private information set to defaults.
        """
        return PlayerState(None,
                           name=self.name,
                           food_bag=None,
                           hand=None,
                           species=self.species)

    def choose(self, before, after):
        """
        Asks this player's strategy interface for their actions given
        the list of species of player's before and after them.
        :param before: List of List of Species where each list of Species
        represents the species boards owned by one player before this one.
        :param after: List of List of Species where each list of Species
        represents the species boards owned by one player after this one.
        :return: An Action representing all actions thie player will make
        this round.
        """
        return self.interface.choose(Choice(self, before, after))

    def next_feeding(self, wh, opponents):
        """
        Asks this player's strategy interface for the feeding choice they
        would like to make.
        :param wh: The number of food tokens in the watering hole.
        :param opponents: list of PlayerState containing all other players.
        :return: A Feeding representing the player's desired feeding choice.
        """
        return self.interface.next_feeding(self, wh, opponents)

    def trait_trigger(self, traitname, effect):
        """
        Applies effect to each species this player owns with the given traitname.
        :param traitname: A String trait name.
        :param effect: Function which takes in a species and modifies it accordingly.
        """
        for species in self.species:
            if traitname in species.traits:
                effect(species)

    def trigger_trait_feeding(self, traitname, wh):
        """
        Feeds all of this player's species with the given trait
        :param traitname: The trait to trigger the feeding.
        :param wh: The number of food tokens in the watering hole.
        """
        for species in self.species:
            if traitname in species.traits:
                wh = self.feed(species, wh)
        return wh

    def trigger_fertile(self):
        """
        Increases the population of all fertile species this player owns.
        """
        self.trait_trigger("fertile", lambda spec: spec.breed())

    def trigger_long_neck(self, wh):
        """
        Feeds all long-neck species this player owns one food token.
        :param wh: The number of food tokens in the watering hole.
        """
        return self.trigger_trait_feeding("long-neck", wh)

    def trigger_scavenging(self, wh):
        """
        Feeds all scavenging species this player owns one food token.
        :param wh: The number of food tokens in the watering hole.
        """
        return self.trigger_trait_feeding("scavenger", wh)

    def trigger_fat_food(self):
        """
        Moves fat_storage food to the food value for all of this player's
        species with the fat-tissue trait.
        """
        self.trait_trigger("fat-tissue", lambda spec: spec.digest_fat())

    def remove_species(self, species):
        """
        Removes the given species from this player's list of species.
        """
        self.species.remove(species)

    def feed(self, species, wh):
        """
        Feeds the given species food tokens from the watering hole. Accounts for
        foraging food amounts as well as cooperation feeding.
        :param species: The species to be fed.
        :param wh: The number of food tokens in the watering hole.
        """
        before_eating = species.food

        wh = self.give_food(species, wh)
        if "foraging" in species.traits:
            wh = self.give_food(species, wh)

        tokens_eaten = species.food - before_eating
        for _ in range(tokens_eaten):
            wh = self.cooperate(species, wh)

        return wh

    def cooperate(self, species, wh):
        """
        Triggers cooperation for the given species if it has the cooperation trait.
        :param species: The species cooperating.
        :param wh: The number of food tokens in the watering hole.
        """
        if wh >= 1:
            species_index = self.species.index(species)
            right_neighbor = (False if species_index == len(self.species) - 1
                              else self.species[species_index + 1])
            if "cooperation" in species.traits and right_neighbor:
                wh = self.feed(right_neighbor, wh)
        return wh

    def give_food(self, species, wh):
        """
        Gives the given species one food token from the watering hole if possible.
        :param species: The Species to be fed.
        :param wh: Number of food tokens in the watering hole.
        """
        if species.population - species.food >= 1 and wh >= 1:
            species.food += 1
            wh -= 1
        return wh

    def move_food_to_bag(self):
        """
        Moves food tokens from all of this player's species to the food bag.
        """
        for species in self.species:
            self.food_bag += species.food
            species.food = 0

    def kill(self, species):
        """
        Reduces the population of the given species by one.
        """
        species.kill()
        if species.is_extinct():
            self.species.remove(species)
            return True
        return False
