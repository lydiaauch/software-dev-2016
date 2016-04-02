import copy
import unittest
import test_utils
from dealer import *
from species import Species
from traitcard import TraitCard
from player import Player
from convert_tests import TestConvert

class TestDealer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        test_utils.setup()

    def step4(self, changes, actions):
        before = copy.deepcopy(self.dealer)
        self.dealer.step4(actions)
        self.check_dealer(before, self.dealer, changes)

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
        self.dealer.player_sets[0]['state'].name = 0
        self.dealer.player_sets[1]['state'].name = 1
        self.dealer.player_sets[2]['state'].name = 2
        self.dealer.player_sets[3]['state'].name = 3
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

        self.assertEqual(Dealer.carnivore_targets(self.species_3, list_of_opponents),
                        [self.species_1])

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

        changes = {
            "watering_hole": 9,
            "current_player_index": 3,
            "players": { 2: { "species": { 0: {"food": 4}}},
                         0: { "species": { 0: {"population": 3, "food": 3}}}}
        }
        self.feed1(changes)

    def test_feed_1_cant_feed(self):
        self.species_3.food = 4
        changes = {
            "current_player_index": 3,
            "players": { 2: { "species": { 0: {"food": 4}}}}
        }
        self.feed1(changes)

    def test_feed_1_no_wh_food(self):
        # TODO: should the player index remain the same or change even when there
        # is no food to eat
        self.dealer.watering_hole = 0
        changes = {"current_player_index": 2}

        self.feed1(changes)

    def test_feed_1_scavenger(self):
        self.species_3.traits.append(TraitCard("carnivore"))
        self.species_4.traits.append(TraitCard("scavenger"))
        self.species_2.traits.append(TraitCard("climbing"))
        self.species_4.traits.append(TraitCard("climbing"))
        self.species_5.traits.append(TraitCard("climbing"))

        changes = {
            "watering_hole": 8,
            "current_player_index": 3,
            "players": { 2: { "species": { 0: {"food": 4}}},
                         3: { "species": { 0: {"food": 4}}},
                         0: { "species": { 0: {"food": 3, "population": 3}}}}
        }
        self.feed1(changes)

    def test_feed_1_double_foraging(self):
        self.species_3.traits.append(TraitCard("foraging"))
        self.species_3.food = 1

        changes = {
            "watering_hole": 8,
            "current_player_index": 3,
            "players": { 2: { "species": { 0: {"food": 3}}}}
        }
        self.feed1(changes)

    def test_feed1_foraging_cooperator_food_run_out(self):
        self.species_4.traits = [TraitCard("foraging"), TraitCard("cooperation")]
        self.species_4.food = 0
        self.species_5.food = 0
        self.dealer.current_player_index = 3
        self.dealer.watering_hole = 3
        changes = {
            "watering_hole": 0,
            "current_player_index": 0,
            "players": { 3: { "species": {0: { "food": 2 },
                                          1: { "food": 1 }}}}
        }
        self.feed1(changes)

    def test_feed1_foraging_cooperator_enough_food(self):
        self.species_4.traits = [TraitCard("foraging"), TraitCard("cooperation")]
        self.species_4.food = 0
        self.species_5.food = 0
        self.dealer.current_player_index = 3
        self.dealer.watering_hole = 4
        changes = {
            "watering_hole": 0,
            "current_player_index": 0,
            "players": { 3: { "species": {0: { "food": 2 },
                                          1: { "food": 2 }}}}
        }
        self.feed1(changes)

    def test_feed_1_foraging(self):
        self.species_3.traits.append(TraitCard("foraging"))
        self.species_3.food = 3

        changes = {
            "watering_hole": 9,
            "current_player_index": 3,
            "players": { 2: { "species": { 0: {"food": 4}}}}
        }
        self.feed1(changes)

    def test_feed_1_cooperation(self):
        self.dealer.current_player_index = 3
        self.species_4.traits.append(TraitCard("cooperation"))
        self.species_5.food = 1

        changes = {
            "watering_hole": 8,
            "current_player_index": 0,
            "players": { 3: { "species": { 0: {"food": 4},
                                           1: {"food": 2}}}}
        }
        self.feed1(changes)

    def test_feed_1_scavenger_cooperation(self):
        self.species_3.traits.append(TraitCard("carnivore"))
        self.species_4.traits.append(TraitCard("climbing"))
        self.species_4.traits.append(TraitCard("cooperation"))
        self.species_4.traits.append(TraitCard("scavenger"))
        self.species_2.traits.append(TraitCard("climbing"))
        self.species_5.traits.append(TraitCard("climbing"))
        self.species_5.food = 2

        changes = {
            "watering_hole": 7,
            "current_player_index": 3,
            "players": {0: { "species": { 0: {"food": 3, "population": 3}}},
                        2: { "species": { 0: {"food": 4}}},
                        3: { "species": { 0: {"food": 4},
                                          1: {"food": 3}}}}
        }
        self.feed1(changes)

    def test_feed_1_cooperation_chain(self):
        self.dealer.player_sets[3]['state'].species.append(self.species_3)
        self.dealer.current_player_index = 3
        self.species_4.traits.append(TraitCard("cooperation"))
        self.species_5.traits.append(TraitCard("cooperation"))
        self.species_5.food = 1
        self.species_3.food = 0

        changes = {
            "watering_hole": 7,
            "current_player_index": 0,
            "players": { 3: { "species": { 0: {"food": 4},
                                           1: {"food": 2},
                                           2: {"food": 1}}},
                         2: { "species": { 0: {"food": 1}}}}
        }
        self.feed1(changes)

    def test_feed_1_carnivore_foraging(self):
        self.species_3.food = 0
        self.species_3.traits.append(TraitCard("carnivore"))
        self.species_3.traits.append(TraitCard("foraging"))
        self.species_2.traits.append(TraitCard("climbing"))
        self.species_4.traits.append(TraitCard("climbing"))
        self.species_5.traits.append(TraitCard("climbing"))

        changes = {
            "watering_hole": 8,
            "current_player_index": 3,
            "players": { 2: { "species": { 0: {"food": 2}}},
                         0: { "species": { 0: {"food": 3, "population": 3}}}}
        }
        self.feed1(changes)

    def test_feed_1_horns(self):
        self.species_3.food = 0
        self.species_3.traits.append(TraitCard("carnivore"))
        self.species_1.traits.append(TraitCard("horns"))
        self.species_2.traits.append(TraitCard("climbing"))
        self.species_4.traits.append(TraitCard("climbing"))
        self.species_5.traits.append(TraitCard("climbing"))

        changes = {
            "watering_hole": 9,
            "current_player_index": 3,
            "players": { 2: { "species": { 0: {"food": 1, "population": 3}}},
                         0: { "species": { 0: {"food": 3, "population": 3}}}}
        }
        self.feed1(changes)

    def test_feed_1_horns_no_food(self):
        self.species_3.traits.append(TraitCard("carnivore"))
        self.species_1.traits.append(TraitCard("horns"))
        self.species_2.traits.append(TraitCard("climbing"))
        self.species_4.traits.append(TraitCard("climbing"))
        self.species_5.traits.append(TraitCard("climbing"))

        changes = {
            "watering_hole": 10,
            "current_player_index": 3,
            "players": { 2: { "species": { 0: {"food": 3, "population": 3}}},
                         0: { "species": { 0: {"food": 3, "population": 3}}}}
        }
        self.feed1(changes)

    def test_extinction(self):
        self.dealer.deck.append(TraitCard("carnivore", -5))
        self.species_3.traits.append(TraitCard("carnivore"))
        self.species_2.traits.append(TraitCard("climbing"))
        self.species_4.traits.append(TraitCard("climbing"))
        self.species_5.traits.append(TraitCard("climbing"))
        self.species_1.population = 1
        changes = {
            "watering_hole": 9,
            "current_player_index": 3,
            "deck": [],
            "players": { 2: { "species": { 0: {"food": 4}}},
                         0: { "species": { 0: "Extinct"},
                              "hand": [TraitCard("carnivore", -5)]}}
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
