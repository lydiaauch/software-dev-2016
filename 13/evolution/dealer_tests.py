import copy
import unittest
import test_utils
from dealer import *
from species import Species
from traitcard import TraitCard
from player import Player
from convert_tests import TestConvert
from actions import *


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
        self.dealer.players[0].name = 0
        self.dealer.players[1].name = 1
        self.dealer.players[2].name = 2
        self.dealer.players[3].name = 3
        self.dealer.current_player_index = 2

        self.species_1 = Species(4, 4, 4)
        self.species_2 = Species(4, 4, 4)
        self.species_3 = Species(4, 3, 3)
        self.species_4 = Species(4, 3, 3)
        self.species_5 = Species(3, 3, 3)
        self.species_list = [self.species_1, self.species_2, self.species_3,
                             self.species_4, self.species_5]

        self.dealer.players[0].species = [self.species_1]
        self.dealer.players[1].species = [self.species_2]
        self.dealer.players[2].species = [self.species_3]
        self.dealer.players[3].species = [self.species_4, self.species_5]

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
        self.species_3.traits = ["carnivore"]
        self.species_2.traits = ["climbing"]
        self.species_4.traits = ["climbing"]
        self.species_5.traits = ["climbing"]

        self.assertEqual(Dealer.carnivore_targets(self.species_3, list_of_opponents),
                         [self.species_1])

        self.species_1.traits = ["climbing"]
        self.assertEqual(Dealer.carnivore_targets(self.species_3, list_of_opponents), [])

    def test_auto_eat_fat_tissue(self):
        self.dealer.current_player_index = 2
        self.species_3.traits = ["fat-tissue"]
        self.species_3.fat_storage = 0
        auto_eat = self.dealer.auto_eat()
        self.assertEqual(auto_eat.species_index, 0)
        self.assertEqual(auto_eat.food_requested, 3)

    def test_auto_eat_herbivore(self):
        self.species_3.traits = []
        self.species_3.food = 2
        self.assertEqual(self.dealer.auto_eat().species_index, 0)

    def test_auto_eat_carnivore(self):
        self.species_3.traits = ["carnivore"]
        self.assertIsNone(self.dealer.auto_eat())

        self.species_2.traits = ["climbing"]
        self.species_4.traits = ["climbing"]
        self.species_5.traits = ["climbing"]

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
            "players": {2: {"species": {0: {"food": 4}}}}
        }
        self.feed1(changes)

    def test_feed_1_fatty(self):
        # current player is feeding fat-tissue species
        self.species_3.traits = ["fat-tissue"]
        changes = {
            "watering_hole": 7,
            "current_player_index": 3,
            "players": {2: {"species": {0: {"food": 3, "fat_storage": 3}}}}
        }
        self.feed1(changes)

    def test_feed_1_carnivore(self):
        self.species_3.traits = ["carnivore"]
        self.species_2.traits = ["climbing"]
        self.species_4.traits = ["climbing"]
        self.species_5.traits = ["climbing"]

        changes = {
            "watering_hole": 9,
            "current_player_index": 3,
            "players": {2: {"species": {0: {"food": 4}}},
                        0: {"species": {0: {"population": 3, "food": 3}}}}
        }
        self.feed1(changes)

    def test_feed_1_cant_feed(self):
        self.species_3.food = 4
        changes = {
            "current_player_index": 3,
            "players": {2: {"species": {0: {"food": 4}}}}
        }
        self.feed1(changes)

    def test_feed_1_no_wh_food(self):
        # TODO: should the player index remain the same or change even when there
        # is no food to eat
        self.dealer.watering_hole = 0
        changes = {"current_player_index": 2}

        self.feed1(changes)

    def test_feed_1_scavenger(self):
        self.species_3.traits.append("carnivore")
        self.species_4.traits.append("scavenger")
        self.species_2.traits.append("climbing")
        self.species_4.traits.append("climbing")
        self.species_5.traits.append("climbing")

        changes = {
            "watering_hole": 8,
            "current_player_index": 3,
            "players": {2: {"species": {0: {"food": 4}}},
                        3: {"species": {0: {"food": 4}}},
                        0: {"species": {0: {"food": 3, "population": 3}}}}
        }
        self.feed1(changes)

    def test_feed_1_double_foraging(self):
        self.species_3.traits.append("foraging")
        self.species_3.food = 1

        changes = {
            "watering_hole": 8,
            "current_player_index": 3,
            "players": {2: {"species": {0: {"food": 3}}}}
        }
        self.feed1(changes)

    def test_feed1_foraging_cooperator_food_run_out(self):
        self.species_4.traits = ["foraging", "cooperation"]
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
        self.species_4.traits = ["foraging", "cooperation"]
        self.species_4.food = 0
        self.species_5.food = 0
        self.dealer.current_player_index = 3
        self.dealer.watering_hole = 4
        changes = {
            "watering_hole": 0,
            "current_player_index": 0,
            "players": {3: {"species": {0: {"food": 2},
                                        1: {"food": 2}}}}
        }
        self.feed1(changes)

    def test_feed_1_foraging(self):
        self.species_3.traits.append("foraging")
        self.species_3.food = 3

        changes = {
            "watering_hole": 9,
            "current_player_index": 3,
            "players": {2: {"species": {0: {"food": 4}}}}
        }
        self.feed1(changes)

    def test_feed_1_cooperation(self):
        self.dealer.current_player_index = 3
        self.species_4.traits.append("cooperation")
        self.species_5.food = 1

        changes = {
            "watering_hole": 8,
            "current_player_index": 0,
            "players": {3: {"species": {0: {"food": 4},
                                        1: {"food": 2}}}}
        }
        self.feed1(changes)

    def test_feed_1_scavenger_cooperation(self):
        self.species_3.traits.append("carnivore")
        self.species_4.traits.append("climbing")
        self.species_4.traits.append("cooperation")
        self.species_4.traits.append("scavenger")
        self.species_2.traits.append("climbing")
        self.species_5.traits.append("climbing")
        self.species_5.food = 2

        changes = {
            "watering_hole": 7,
            "current_player_index": 3,
            "players": {0: {"species": {0: {"food": 3, "population": 3}}},
                        2: {"species": {0: {"food": 4}}},
                        3: {"species": {0: {"food": 4},
                                        1: {"food": 3}}}}
        }
        self.feed1(changes)

    def test_feed_1_cooperation_chain(self):
        self.dealer.players[3].species.append(self.species_3)
        self.dealer.current_player_index = 3
        self.species_4.traits.append("cooperation")
        self.species_5.traits.append("cooperation")
        self.species_5.food = 1
        self.species_3.food = 0

        changes = {
            "watering_hole": 7,
            "current_player_index": 0,
            "players": {3: {"species": {0: {"food": 4},
                                        1: {"food": 2},
                                        2: {"food": 1}}},
                        2: {"species": {0: {"food": 1}}}}
        }
        self.feed1(changes)

    def test_feed_1_carnivore_foraging(self):
        self.species_3.food = 0
        self.species_3.traits.append("carnivore")
        self.species_3.traits.append("foraging")
        self.species_2.traits.append("climbing")
        self.species_4.traits.append("climbing")
        self.species_5.traits.append("climbing")

        changes = {
            "watering_hole": 8,
            "current_player_index": 3,
            "players": {2: {"species": {0: {"food": 2}}},
                        0: {"species": {0: {"food": 3, "population": 3}}}}
        }
        self.feed1(changes)

    def test_feed_1_horns(self):
        self.species_3.food = 0
        self.species_3.traits.append("carnivore")
        self.species_1.traits.append("horns")
        self.species_2.traits.append("climbing")
        self.species_4.traits.append("climbing")
        self.species_5.traits.append("climbing")

        changes = {
            "watering_hole": 9,
            "current_player_index": 3,
            "players": {2: {"species": {0: {"food": 1, "population": 3}}},
                        0: {"species": {0: {"food": 3, "population": 3}}}}
        }
        self.feed1(changes)

    def test_feed_1_horns_no_food(self):
        self.species_3.traits.append("carnivore")
        self.species_1.traits.append("horns")
        self.species_2.traits.append("climbing")
        self.species_4.traits.append("climbing")
        self.species_5.traits.append("climbing")

        changes = {
            "watering_hole": 10,
            "current_player_index": 3,
            "players": {2: {"species": {0: {"food": 3, "population": 3}}},
                        0: {"species": {0: {"food": 3, "population": 3}}}}
        }
        self.feed1(changes)

    def test_extinction(self):
        self.dealer.deck.append(TraitCard("carnivore", -5))
        self.species_3.traits.append("carnivore")
        self.species_2.traits.append("climbing")
        self.species_4.traits.append("climbing")
        self.species_5.traits.append("climbing")
        self.species_1.population = 1
        changes = {
            "watering_hole": 9,
            "current_player_index": 3,
            "deck": [],
            "players": {2: {"species": {0: {"food": 4}}},
                        0: {"species": {0: "Extinct"},
                            "hand": [TraitCard("carnivore", -5)]}}
        }
        self.feed1(changes)

    def test_player_can_feed(self):
        self.assertFalse(self.dealer.player_can_feed(self.dealer.players[0]))
        self.assertTrue(self.dealer.player_can_feed(self.dealer.players[2]))

        self.species_4.traits.append("carnivore")
        self.species_1.traits.append("climbing")
        self.species_2.traits.append("climbing")
        self.species_3.traits.append("climbing")
        self.species_5.traits.append("climbing")
        self.assertFalse(self.dealer.player_can_feed(self.dealer.players[3]))

    def test_step4_simple(self):
        self.dealer.players[0].hand = [TraitCard("burrowing", food_points=0)]
        self.dealer.players[1].hand = [TraitCard("burrowing", food_points=3)]
        self.dealer.players[2].hand = [TraitCard("burrowing", food_points=2)]
        self.dealer.players[3].hand = [TraitCard("burrowing", food_points=1)]

        actions = [Action(0, [], [], [], []), Action(0, [], [], [], []),
                   Action(0, [], [], [], []), Action(0, [], [], [], [])]

        changes = {
            "watering_hole": 14,
            "current_player_index": 0,
            "players": {0: {"hand": []},
                        1: {"hand": []},
                        2: {"hand": [], "species": {0: {"food": 4}}},
                        3: {"hand": [], "species": {0: {"food": 4}}}}
        }

        self.step4(changes, actions)

    def test_step4_GP(self):
        self.dealer.players[0].hand = [TraitCard("burrowing", food_points=0),
                                       TraitCard("climbing", food_points=1)]
        self.dealer.players[1].hand = [TraitCard("burrowing", food_points=3)]
        self.dealer.players[2].hand = [TraitCard("burrowing", food_points=2)]
        self.dealer.players[3].hand = [TraitCard("burrowing", food_points=1)]

        actions = [Action(0, [PopGrow(0, 1)], [], [], []), Action(0, [], [], [], []),
                   Action(0, [], [], [], []), Action(0, [], [], [], [])]

        changes = {
            "watering_hole": 13,
            "current_player_index": 1,
            "players": {0: {"hand": [], "species": {0: {"food": 5, "population": 5}}},
                        1: {"hand": []},
                        2: {"hand": [], "species": {0: {"food": 4}}},
                        3: {"hand": [], "species": {0: {"food": 4}}}}
        }

        self.step4(changes, actions)

    def test_step4_GB(self):
        self.dealer.players[0].hand = [TraitCard("burrowing", food_points=0),
                                       TraitCard("climbing", food_points=1)]
        self.dealer.players[1].hand = [TraitCard("burrowing", food_points=3)]
        self.dealer.players[2].hand = [TraitCard("burrowing", food_points=2)]
        self.dealer.players[3].hand = [TraitCard("burrowing", food_points=1)]

        actions = [Action(0, [], [BodyGrow(0, 1)], [], []), Action(0, [], [], [], []),
                   Action(0, [], [], [], []), Action(0, [], [], [], [])]

        changes = {
            "watering_hole": 14,
            "current_player_index": 0,
            "players": {0: {"hand": [], "species": {0: {"body": 5}}},
                        1: {"hand": []},
                        2: {"hand": [], "species": {0: {"food": 4}}},
                        3: {"hand": [], "species": {0: {"food": 4}}}}
        }

        self.step4(changes, actions)

    def test_step4_RT(self):
        self.species_1.traits.append("long-neck")
        self.dealer.players[0].hand = [TraitCard("burrowing", food_points=0),
                                       TraitCard("climbing", food_points=1)]
        self.dealer.players[1].hand = [TraitCard("burrowing", food_points=3)]
        self.dealer.players[2].hand = [TraitCard("burrowing", food_points=2)]
        self.dealer.players[3].hand = [TraitCard("burrowing", food_points=1)]

        actions = [Action(0, [], [], [], [ReplaceTrait(0, 0, 1)]), Action(0, [], [], [], []),
                   Action(0, [], [], [], []), Action(0, [], [], [], [])]

        changes = {
            "watering_hole": 14,
            "current_player_index": 0,
            "players": {0: {"hand": [],
                            "species": {0: {"traits": ["climbing"]}}},
                        1: {"hand": []},
                        2: {"hand": [], "species": {0: {"food": 4}}},
                        3: {"hand": [], "species": {0: {"food": 4}}}}
        }

        self.step4(changes, actions)

    def test_step4_BT(self):
        self.dealer.players[0].hand = [TraitCard("burrowing", food_points=0),
                                       TraitCard("climbing", food_points=1),
                                       TraitCard("climbing", food_points=2)]
        self.dealer.players[1].hand = [TraitCard("burrowing", food_points=3)]
        self.dealer.players[2].hand = [TraitCard("burrowing", food_points=2)]
        self.dealer.players[3].hand = [TraitCard("burrowing", food_points=1)]

        actions = [Action(0, [], [], [BoardAddition(0, [1, 2])], []), Action(0, [], [], [], []),
                   Action(0, [], [], [], []), Action(0, [], [], [], [])]

        changes = {
            "watering_hole": 13,
            "current_player_index": 1,
            "players": {0: {"hand": [],
                            "species": {1: {"body": 0,
                                            "food": 1,
                                            "fat_storage": 0,
                                            "population": 1,
                                            "traits": ["climbing", "climbing"]}}},
                        1: {"hand": []},
                        2: {"hand": [], "species": {0: {"food": 4}}},
                        3: {"hand": [], "species": {0: {"food": 4}}}}
        }

        self.step4(changes, actions)

    def test_print_results(self):
        self.dealer.players[0].food_bag = 0
        self.dealer.players[1].food_bag = 1
        self.dealer.players[2].food_bag = 2
        self.dealer.players[3].food_bag = 3
        expected_str = "1 player id: 3 score: 3\n2 player id: 2 score: 2\n3 player id: 1 score: 1\n4 player id: 0 score: 0\n"
        self.assertEqual(self.dealer.print_results(), expected_str)

    def test_create_deck(self):
        self.dealer.create_deck()
        for trait in TraitCard.traits:
            cards = [card for card in self.dealer.deck if card.trait == trait]
            if trait == "carnivore":
                self.assertEqual(len(cards), 17)
            else:
                self.assertEqual(len(cards), 7)
        self.assertEqual(len(self.dealer.deck), 122)

    def test_compare_cards(self):
        card0 = TraitCard("climbing", 0)
        card1 = TraitCard("burrowing", 3)
        card2 = TraitCard("climbing", -1)
        cards = [card0, card1, card2]
        cards.sort(Dealer.compare_cards)
        self.assertEqual(cards, [card1, card2, card0])
        self.assertEqual(Dealer.compare_cards(card0, card1), 1)
        self.assertEqual(Dealer.compare_cards(card1, card2), -1)
        self.assertEqual(Dealer.compare_cards(card0, card2), 1)

    def test_make_initial_species(self):
        self.dealer.players[0].species = []
        before = copy.deepcopy(self.dealer)
        self.dealer.make_initial_species()
        changes = {
            "players": {
                0: {"species": {
                    0: {"food": 0, "body": 0, "population": 1,
                        "traits": [], "fat_storage": 0}}}}}
        self.check_dealer(before, self.dealer, changes)

    def test_min_deck_size(self):
        self.assertEqual(self.dealer.min_deck_size(), 17)
        self.dealer.players[0].species.append(Species())
        self.assertEqual(self.dealer.min_deck_size(), 18)
        self.dealer.players.append(PlayerState(Player))
        self.assertEqual(self.dealer.min_deck_size(), 21)

    def test_reduce_species_pop(self):
        before = copy.deepcopy(self.dealer)
        self.dealer.reduce_species_pop()
        changes = {
            "players": {
                2: {"species": {0: {"population": 3}}},
                3: {"species": {0: {"population": 3}}}}
        }
        self.check_dealer(before, self.dealer, changes)

    def test_reduce_species_pop_extinct(self):
        self.dealer.players[0].species[0].food = 0
        self.dealer.deck = ["climbing", "burrowing", "long-neck"]
        before = copy.deepcopy(self.dealer)
        self.dealer.reduce_species_pop()
        changes = {
            "deck": ["long-neck"],
            "players": {
                0: {"hand": ["climbing", "burrowing"],
                    "species": {0: "Extinct"}},
                2: {"species": {0: {"population": 3}}},
                3: {"species": {0: {"population": 3}}}}
        }
        self.check_dealer(before, self.dealer, changes)

    def test_move_food(self):
        before = copy.deepcopy(self.dealer)
        self.dealer.move_food()
        changes = {
            "players": {
                0: {"food_bag": 4,
                    "species": {0: {"food": 0}}},
                1: {"food_bag": 4,
                    "species": {0: {"food": 0}}},
                2: {"food_bag": 3,
                    "species": {0: {"food": 0}}},
                3: {"food_bag": 6,
                    "species": {0: {"food": 0}, 1: {"food": 0}}}}
        }
        self.check_dealer(before, self.dealer, changes)

if __name__ == '__main__':
    unittest.main()
