import copy
import unittest
from dealer import *
from species import Species
from traitcard import TraitCard
from player import Player
from convert_tests import TestConvert

class TestDealer(unittest.TestCase):
    def check_dealer(self, before, after, changes):
        """
        Checks that all aspects of self.dealer are the same except for the changes
        specified in the changes after calling dealer.method. changes is a subset of
        {
            "watering_hole": Number,
            "current_player_index": Number,
            "deck": [TraitCard, ...] Where a TraitCard is an [Number, String]
            "players": {Number: PlayerConfig, ...} where the player configuration
                                                   describes the changes to the
                                                   player state at the given index
        }
        #TODO: index players by id.
        """
        self.check_attribute(before, after, changes, "watering_hole")
        self.check_attribute(before, after, changes, "current_player_index")
        self.check_attribute(before, after, changes, "deck")
        for i in range(len(before.player_states())):
            if i in changes["players"]:
                self.check_player(before.player_state(i), after.player_state(i), changes["players"][i])
            else:
                self.check_player(before.player_state(i), after.player_state(i), {})

    def check_player(self, before, after, changes):
        """
        Checks that all aspects of the given player are the same except for changes
        specified in the configuration. A changes is a subset of the dictionary
        {
            "name": Any,
            "food_bag": Number,
            "hand": [TraitCard, ...], Where a TraitCard is an [Number, String]
            "species": {Number: SpeciesChanges, ...} where the species configuration
                                                     describes the changes to species
                                                     at the given index, or is the
                                                     string "Extinct" if the slot
                                                     is now empty.
        }
        """
        self.check_attribute(before, after, changes, "name")
        self.check_attribute(before, after, changes, "food_bag")
        self.check_attribute(before, after, changes, "hand")
        i = 0 #before species_list index
        j = 0 #after species_list index
        while i < len(before.species) and j < len(after.species):
            if "species" in changes and i in changes["species"]:
                if changes["species"][i] == "Extinct":
                    i += 1
                    continue
                else:
                    self.check_species(before.species[i], after.species[j], changes["species"][i])
            else:
                self.check_species(before.species[i], after.species[j], {})

            i += 1
            j += 1

        # TODO: Species list lengths are not checked.
        # self.assertTrue(i == len(before.species) and j == len(after.species))

    def check_species(self, before, after, changes):
        """
        Checks that all aspects of the given species are the same except for changes
        specified in the configuration. A changes is a subset of the dictionary
        {
            "poplation": Number,
            "food": Number,
            "body": Number,
            "fat_storage": Number,
            "traits": [String, ...]
        }
        """
        self.check_attribute(before, after, changes, "population")
        self.check_attribute(before, after, changes, "food")
        self.check_attribute(before, after, changes, "body")
        self.check_attribute(before, after, changes, "fat_storage")
        self.check_attribute(before, after, changes, "traits")

    def check_attribute(self, before, after, changes, attribute):
        """
        Checks if a given attribute has changed from the before to after objects.
        :param before: The object to check before the changes applied.
        :param after: The object to check after the changes applied.
        :param changes: Dictionary where the keys are the names of the attributes
        that should have changed and the values are the expected values.
        :param attribute: The string name of the attribute to check.
        """
        if attribute in changes:
            self.assertEqual(getattr(after, attribute), changes[attribute])
        else:
            self.assertEqual(getattr(after, attribute), getattr(before, attribute))

    def feed1(self, changes):
        """
        Checks that only attributes described in the changes dictionary have been
        modified.
        :param changes: See check_dealer changes docstring.
        """
        before = copy.deepcopy(self.dealer)
        self.dealer.feed1()
        self.check_dealer(before, self.dealer, changes)

    def setUp(self):
        self.dealer = Dealer([Player(), Player(), Player(), Player()])
        self.dealer.watering_hole = 10
        self.dealer.player_sets[0]['state'].name = 0;
        self.dealer.player_sets[1]['state'].name = 1;
        self.dealer.player_sets[2]['state'].name = 2;
        self.dealer.player_sets[3]['state'].name = 3;
        self.dealer.current_player_index = 2

        self.species_1 = Species(4, 4, 4)
        self.species_2 = Species(4, 4, 4)
        self.species_3 = Species(4, 3, 3)
        self.species_4 = Species(4, 3, 3)
        self.species_5 = Species(3, 3, 3)
        self.species_list = [self.species_1, self.species_2, self.species_3,
                             self.species_4, self.species_5]

        self.dealer.player_sets[0]['state'].species = [self.species_1]
        self.dealer.player_sets[1]['state'].species = [self.species_2]
        self.dealer.player_sets[2]['state'].species = [self.species_3]
        self.dealer.player_sets[3]['state'].species = [self.species_4, self.species_5]


    def test_check_for_hungries(self):
        hungries = self.dealer.check_for_hungries(self.species_list)
        self.assertEqual(2, len(hungries))
        self.assertTrue(TestConvert.species_soft_eq(self.species_4, hungries[0]))

    def test_opponents(self):
        opponents = self.dealer.opponents()
        self.assertEqual(3, len(opponents))

        opponents_name_2 = filter(lambda p: p.name == 2, opponents)
        self.assertEqual(0, len(opponents_name_2))

    def test_carnivore_targets(self):
        list_of_opponents = self.dealer.opponents()
        self.species_3.traits = [TraitCard("carnivore")]
        self.species_2.traits = [TraitCard("climbing")]
        self.species_4.traits = [TraitCard("climbing")]
        self.species_5.traits = [TraitCard("climbing")]

        self.assertEqual(Dealer.carnivore_targets(self.species_3, list_of_opponents), [self.species_1])

        self.species_1.traits = [TraitCard("climbing")]
        self.assertEqual(Dealer.carnivore_targets(self.species_3, list_of_opponents), [])

    def test_auto_eat_fat_tissue(self):
        self.dealer.current_player_index = 2
        self.species_3.traits= [TraitCard("fat-tissue")]
        self.species_3.fat_storage = 0
        auto_eat = self.dealer.auto_eat()
        self.assertEqual(auto_eat.species_index, 0)
        self.assertEqual(auto_eat.food_requested, 3)

    def test_auto_eat_herbivore(self):
        self.species_3.traits = []
        self.species_3.food = 2
        self.assertEqual(self.dealer.auto_eat().species_index, 0)

    def test_auto_eat_carnivore(self):
        self.species_3.traits = [TraitCard("carnivore")]
        self.assertIsNone(self.dealer.auto_eat())

        self.species_2.traits = [TraitCard("climbing")]
        self.species_4.traits = [TraitCard("climbing")]
        self.species_5.traits = [TraitCard("climbing")]

        auto_eat = self.dealer.auto_eat()
        self.assertEqual(auto_eat.attacker_index, 0)
        self.assertEqual(auto_eat.target_index, 0)
        self.assertEqual(auto_eat.defender_index, 0)

        self.species_3.food = 4
        self.assertIsNone(self.dealer.auto_eat())

    def test_feed_1_herbivore(self):
        # current player has single hungry herbivore -> auto_eat
        changes = {
            "watering_hole": 9,
            "current_player_index": 3,
            "players": { 2: { "species": { 0: {"food": 4}}}}
        }
        self.feed1(changes)

    def test_feed_1_fatty(self):
        # current player is feeding fat-tissue species
        self.species_3.traits = [TraitCard("fat-tissue")]
        changes = {
            "watering_hole": 7,
            "current_player_index": 3,
            "players": { 2: { "species": { 0: {"food": 3, "fat_storage": 3}}}}
        }
        self.feed1(changes)

    def test_feed_1_carnivore(self):
        self.species_3.traits = [TraitCard("carnivore")]
        self.species_2.traits = [TraitCard("climbing")]
        self.species_4.traits = [TraitCard("climbing")]
        self.species_5.traits = [TraitCard("climbing")]

        self.dealer.feed1()
        self.assertEqual(self.dealer.watering_hole, 9)
        self.assertEqual(self.dealer.current_player_index, 3)
        self.assertEqual(self.species_3.food, 4)
        self.assertEqual(self.species_1.population, 3)

    def test_feed_1_cant_feed(self):
        self.dealer.feed1()
        self.assertEqual(self.dealer.current_player_index, 3)

    def test_feed_1_no_wh_food(self):
        self.dealer.watering_hole = 0
        before = copy.deepcopy(self.dealer)
        self.dealer.feed1()
        self.assertEqual(before, self.dealer)


    def test_feed_1_scavenger(self):
        self.species_3.traits.append(TraitCard("carnivore"))
        self.species_4.traits.append(TraitCard("scavenger"))
        self.species_2.traits.append(TraitCard("climbing"))
        self.species_4.traits.append(TraitCard("climbing"))
        self.species_5.traits.append(TraitCard("climbing"))

        self.dealer.feed1()
        self.assertEqual(self.species_3.food, 4)
        self.assertEqual(self.species_4.food, 4)
        self.assertEqual(self.species_1.population, 3)
        self.assertEqual(self.dealer.watering_hole, 8)

    def test_feed_1_double_foraging(self):
        self.species_3.traits.append(TraitCard("foraging"))
        self.species_3.food = 1
        self.dealer.feed1()
        self.assertEqual(self.species_3.food, 3)

    def test_feed_1_foraging(self):
        self.species_3.traits.append(TraitCard("foraging"))
        self.species_3.food = 3
        self.dealer.feed1()
        self.assertEqual(self.species_3.food, 4)

    def test_feed_1_cooperation(self):
        self.dealer.current_player_index = 3
        self.species_4.traits.append(TraitCard("cooperation"))
        self.species_5.food = 1
        self.dealer.feed1()
        self.assertEqual(self.species_4.food, 4)
        self.assertEqual(self.species_5.food, 2)

    def test_feed_1_scavenger_cooperation(self):
        self.species_3.traits.append(TraitCard("carnivore"))
        self.species_4.traits.append(TraitCard("climbing"))
        self.species_4.traits.append(TraitCard("cooperation"))
        self.species_4.traits.append(TraitCard("scavenger"))
        self.species_2.traits.append(TraitCard("climbing"))
        self.species_5.traits.append(TraitCard("climbing"))
        self.species_5.food = 2

        self.dealer.feed1()
        self.assertTrue("cooperation" in self.species_4.trait_names())
        self.assertEqual(self.species_4.food, 4)
        self.assertEqual(self.species_5.food, 3)

    def test_feed_1_cooperation_chain(self):
        self.dealer.player_sets[3]['state'].species.append(self.species_3)
        self.dealer.current_player_index = 3
        self.species_4.traits.append(TraitCard("cooperation"))
        self.species_5.traits.append(TraitCard("cooperation"))
        self.species_5.food = 1
        self.species_3.food = 0
        self.dealer.feed1()
        self.assertEqual(self.species_4.food, 4)
        self.assertEqual(self.species_5.food, 2)
        self.assertEqual(self.species_3.food, 1)

    def test_feed_1_carnivore_foraging(self):
        self.species_3.food = 0
        self.species_3.traits.append(TraitCard("carnivore"))
        self.species_3.traits.append(TraitCard("foraging"))
        self.species_2.traits.append(TraitCard("climbing"))
        self.species_4.traits.append(TraitCard("climbing"))
        self.species_5.traits.append(TraitCard("climbing"))

        self.dealer.feed1()
        self.assertEqual(self.species_3.food, 2)

    def test_feed_1_horns(self):
        self.species_3.food = 0
        self.species_3.traits.append(TraitCard("carnivore"))
        self.species_1.traits.append(TraitCard("horns"))
        self.species_2.traits.append(TraitCard("climbing"))
        self.species_4.traits.append(TraitCard("climbing"))
        self.species_5.traits.append(TraitCard("climbing"))

        self.dealer.feed1()
        self.assertEqual(self.species_3.population, 3)
        self.assertEqual(self.species_3.food, 1)

    def test_feed_1_horns_no_food(self):
        self.species_3.traits.append(TraitCard("carnivore"))
        self.species_1.traits.append(TraitCard("horns"))
        self.species_2.traits.append(TraitCard("climbing"))
        self.species_4.traits.append(TraitCard("climbing"))
        self.species_5.traits.append(TraitCard("climbing"))

        self.dealer.feed1()
        self.assertEqual(self.species_3.population, 3)
        self.assertEqual(self.species_3.food, 3)

    def test_extinction(self):
        self.species_3.traits.append(TraitCard("carnivore"))
        self.species_1.population = 1
        self.species_2.traits.append(TraitCard("climbing"))
        self.species_4.traits.append(TraitCard("climbing"))
        self.species_5.traits.append(TraitCard("climbing"))
        changes = {
            "watering_hole": 9,
            "current_player_index": 3,
            "players": { 2: { "species": { 0: {"food": 4}}},
                         0: { "species": { 0: "Extinct"}}}
        }
        self.feed1(changes)

    def test_player_can_feed(self):
        self.assertFalse(self.dealer.player_can_feed(self.dealer.player_state(0)))
        self.assertTrue(self.dealer.player_can_feed(self.dealer.player_state(2)))

        self.species_4.traits.append(TraitCard("carnivore"))
        self.species_1.traits.append(TraitCard("climbing"))
        self.species_2.traits.append(TraitCard("climbing"))
        self.species_3.traits.append(TraitCard("climbing"))
        self.species_5.traits.append(TraitCard("climbing"))
        self.assertFalse(self.dealer.player_can_feed(self.dealer.player_state(3)))

if __name__ == '__main__':
    unittest.main()
