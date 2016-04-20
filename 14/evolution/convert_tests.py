import unittest
from species import Species
from traitcard import TraitCard
from player_state import PlayerState
from convert import Convert
from player import Player
from choice import Choice
from feeding import *
from actions import *


class TestConvert(unittest.TestCase):
    def setUp(self):
        self.setUp_cards()
        self.setUp_json_species()
        self.setUp_json_players()
        self.setUp_traitcards()
        self.setUp_species()
        self.setUp_players()

    def setUp_cards(self):
        self.jt_1 = "carnivore"
        self.jt_2 = "fat-tissue"
        self.jt_3 = "burrowing"
        self.jt_4 = "climbing"

        self.jtc_1 = [8, "carnivore"]
        self.jtc_2 = [-3, "fat-tissue"]
        self.jtc_3 = [0, "burrowing"]
        self.jtc_4 = [3, "climbing"]
        self.jtc_5 = [-8, "carnivore"]
        self.jtc_6 = [2, "climbing"]

    def setUp_json_species(self):
        self.jSpecies_1 = [["food", 2],
                           ["body", 2],
                           ["population", 2],
                           ["traits", [self.jt_1]]]

        self.jSpecies_2 = [["food", 2],
                           ["body", 3],
                           ["population", 3],
                           ["traits", [self.jt_2]]]

        self.jSpecies_3 = [["food", 2],
                           ["body", 3],
                           ["population", 4],
                           ["traits", [self.jt_3, self.jt_4]]]

        self.jSpecies_4 = [["food", 2],
                           ["body", 2],
                           ["population", 2],
                           ["traits", [self.jt_3, self.jt_4]]]

    def setUp_json_players(self):
        self.jPlayer_1 = [["id", 1],
                          ["species", [self.jSpecies_1]],
                          ["bag", 2]]

        self.jPlayer_2 = [["id", 2],
                          ["species", [self.jSpecies_2]],
                          ["bag", 1],
                          ["cards", [self.jtc_1, self.jtc_2]]]

        self.jPlayer_3 = [["id", 3],
                          ["species", [self.jSpecies_3, self.jSpecies_4]],
                          ["bag", 3],
                          ["cards", [self.jtc_3, self.jtc_4]]]

    def setUp_traitcards(self):
        self.t_1 = "carnivore"
        self.t_2 = "fat-tissue"
        self.t_3 = "burrowing"
        self.t_4 = "climbing"

        self.tc_1 = TraitCard("carnivore", 8)
        self.tc_2 = TraitCard("fat-tissue", -3)
        self.tc_3 = TraitCard("burrowing", 0)
        self.tc_4 = TraitCard("climbing", 3)
        self.tc_5 = TraitCard("carnivore", -8)
        self.tc_6 = TraitCard("climbing", 2)

    def setUp_species(self):
        self.species_1 = Species(2, 2, 2, [self.t_1])
        self.species_2 = Species(3, 2, 3, [self.t_2], 0)
        self.species_3 = Species(4, 2, 3, [self.t_3, self.t_4])
        self.species_4 = Species(2, 2, 2, [self.t_3, self.t_4])

    def setUp_players(self):
        self.player_1 = PlayerState(Player,
                                    name=1,
                                    food_bag=2,
                                    species=[self.species_1])

        self.player_2 = PlayerState(Player,
                                    name=2,
                                    food_bag=1,
                                    species=[self.species_2],
                                    hand=[self.tc_1, self.tc_2])

        self.player_3 = PlayerState(Player,
                                    name=3,
                                    food_bag=3,
                                    species=[self.species_3, self.species_4],
                                    hand=[self.tc_3, self.tc_4])

        self.jConfig_1 = [[self.jPlayer_1, self.jPlayer_2, self.jPlayer_3],
                          42,
                          [self.jtc_5, self.jtc_6]]

    def test_json_to_dealer(self):
        dealer = Convert.json_to_dealer(self.jConfig_1)
        self.assertEqual(len(dealer.players), 3)
        self.assertEqual(dealer.watering_hole, 42)
        self.assertEqual(len(dealer.deck), 2)
        self.assertEqual(dealer.deck[0], self.tc_5)
        self.assertEqual(dealer.deck[1], self.tc_6)

    def test_bad_json_to_dealer_not_enough_players(self):
        self.jConfig_1[0].pop()
        self.assertRaises(AssertionError, Convert.json_to_dealer, self.jConfig_1)

    def test_bad_json_to_dealer_too_many_players(self):
        for i in range(6):
            self.jConfig_1[0].append(self.jPlayer_1)
        self.assertRaises(AssertionError, Convert.json_to_dealer, self.jConfig_1)

    def test_json_to_trait_card(self):
        self.assertEqual(Convert.json_to_trait_card(self.jtc_1), self.tc_1)
        self.assertEqual(Convert.json_to_trait_card(self.jtc_2), self.tc_2)
        self.assertEqual(Convert.json_to_trait_card(self.jtc_3), self.tc_3)
        self.assertEqual(Convert.json_to_trait_card(self.jtc_4), self.tc_4)
        self.assertEqual(Convert.json_to_trait_card(self.jtc_5), self.tc_5)
        self.assertEqual(Convert.json_to_trait_card(self.jtc_6), self.tc_6)

    def test_json_to_species(self):
        self.assertTrue(self.species_soft_eq(Convert.json_to_species(self.jSpecies_1),
                                             self.species_1))
        self.assertTrue(self.species_soft_eq(Convert.json_to_species(self.jSpecies_2),
                                             self.species_2))
        self.assertFalse(self.species_soft_eq(Convert.json_to_species(self.jSpecies_1),
                                              self.species_2))
        self.jSpecies_1[0][1] = -1
        self.assertRaises(AssertionError, Convert.json_to_species, self.jSpecies_1)

    def test_species_to_json(self):
        self.assertEqual(Convert.species_to_json(self.species_1), self.jSpecies_1)
        self.assertNotEqual(Convert.species_to_json(self.species_1), self.jSpecies_2)
        self.species_1.population = -1
        self.assertRaises(AssertionError, Convert.species_to_json, self.species_1)

    def test_json_to_player(self):
        self.assertTrue(self.player_soft_eq(Convert.json_to_player(self.jPlayer_1), self.player_1))
        self.assertTrue(self.player_soft_eq(Convert.json_to_player(self.jPlayer_2), self.player_2))
        self.assertTrue(self.player_soft_eq(Convert.json_to_player(self.jPlayer_3), self.player_3))
        self.assertFalse(self.player_soft_eq(Convert.json_to_player(self.jPlayer_1), self.player_2))
        self.jPlayer_1[0][1] = -1
        self.assertRaises(AssertionError, Convert.json_to_player, self.jPlayer_1)

    def test_player_to_json(self):
        self.assertEqual(Convert.player_to_json(self.player_1), self.jPlayer_1)
        self.assertNotEqual(Convert.player_to_json(self.player_1), self.jPlayer_2)
        self.player_1.food_bag = -1
        self.assertRaises(AssertionError, Convert.player_to_json, self.player_1)

    def test_bad_json_to_player(self):
        bad_json = [["id", 1], ["speciess", [self.jSpecies_1]], ["bag", 2]]
        self.assertRaises(Exception, Convert.json_to_player, bad_json)

    def test_bad_json_to_player_ordering(self):
        bad_json = [["foood", 2], ["body", 2], ["population", 2], ["traits", [self.jt_1]]]
        self.assertRaises(Exception, Convert.json_to_player, bad_json)

    def test_json_to_listof_species(self):
        json = [self.jSpecies_1, self.jSpecies_2]
        actual = Convert.json_to_listof_species(json)
        expected = [self.species_1, self.species_2]
        for (act, exp) in zip(actual, expected):
            TestConvert.species_soft_eq(act, exp)

    def test_json_to_choice_good(self):
        good_json = [[[self.jSpecies_1, self.jSpecies_2]],
                     [[self.jSpecies_3, self.jSpecies_4]]]
        expected = Choice([[self.species_1, self.species_2]],
                          [[self.species_3, self.species_4]])
        actual = Convert.json_to_choice(good_json)
        for i in range(len(expected.before)):
            self.assertTrue(TestConvert.species_list_eq(expected.before[i], actual.before[i]))
        for i in range(len(expected.after)):
            self.assertTrue(TestConvert.species_list_eq(expected.after[i], actual.after[i]))

    def test_json_to_choice_bad(self):
        json = [[[self.jSpecies_1, self.jSpecies_2]],
                [[self.jSpecies_3, "not a species"]]]
        with self.assertRaises(AssertionError):
            Convert.json_to_choice(json)
        json = [[[self.jSpecies_1, self.jSpecies_2]]]
        with self.assertRaises(AssertionError):
            Convert.json_to_choice(json)
        json = 42
        with self.assertRaises(AssertionError):
            Convert.json_to_choice(json)

    def test_json_to_feeding_good(self):
        # :(
        json_abstain = False
        self.assertEqual(Convert.json_to_feeding(json_abstain), AbstainFeeding())
        json_herbivore = 0
        self.assertEqual(Convert.json_to_feeding(json_herbivore), HerbivoreFeeding(0))
        json_fat_tissue = [3, 1]
        self.assertEqual(Convert.json_to_feeding(json_fat_tissue), FatTissueFeeding(3, 1))
        json_carnivore = [3, 2, 1]
        self.assertEqual(Convert.json_to_feeding(json_carnivore), CarnivoreFeeding(3, 2, 1))

    def test_json_to_feeding_bad(self):
        # :)
        bad_json = True
        with self.assertRaises(AssertionError):
            Convert.json_to_feeding(bad_json)
        bad_json = -1
        with self.assertRaises(AssertionError):
            Convert.json_to_feeding(bad_json)
        bad_json = [1, 2, 3, 4, 5]
        with self.assertRaises(AssertionError):
            Convert.json_to_feeding(bad_json)
        bad_json = "HELLO"
        with self.assertRaises(AssertionError):
            Convert.json_to_feeding(bad_json)
        bad_json = [1, 2, -1]
        with self.assertRaises(AssertionError):
            Convert.json_to_feeding(bad_json)

    def test_json_to_player_state_good(self):
        # [Natural,[Species+, ..., Species+], Cards]
        json = [5, [self.jSpecies_1], [self.jtc_1]]
        expected = PlayerState(None, food_bag=5, species=[self.species_1], hand=[self.tc_1])
        self.assertTrue(TestConvert.player_soft_eq(Convert.json_to_player_state(json), expected))
        json = [5, [self.jSpecies_1, self.jSpecies_2], []]
        expected = PlayerState(None, food_bag=5, species=[self.species_1, self.species_2])
        self.assertTrue(TestConvert.player_soft_eq(Convert.json_to_player_state(json), expected))

    def test_json_to_player_state_bad(self):
        json = [5, [self.jSpecies_1], [self.jtc_1], 2]
        with self.assertRaises(AssertionError):
            Convert.json_to_player_state(json)
        json = [[self.jSpecies_1], [self.jtc_1], 2]
        with self.assertRaises(AssertionError):
            Convert.json_to_player_state(json)
        json = [5, [self.jSpecies_1], [self.jtc_1, 2]]
        with self.assertRaises(AssertionError):
            Convert.json_to_player_state(json)
        json = [[self.jSpecies_1, "not a species"], [self.jtc_1]]
        with self.assertRaises(AssertionError):
            Convert.json_to_player_state(json)
        json = "CRASH.. please?"
        with self.assertRaises(AssertionError):
            Convert.json_to_player_state(json)

    def test_validate_action_json_good(self):
        json = [1, [], [], [], []]
        expect = Action(1, [], [], [], [])
        self.assertEqual(Convert.json_to_action(json), expect)
        json = [1, [[0, 0]], [[1, 2]], [[1, 2, 3], [2]], [[4, 5, 6]]]
        expect = Action(1, [PopGrow(0, 0)],
                        [BodyGrow(1, 2)],
                        [BoardAddition(1, [2, 3]), BoardAddition(2)],
                        [ReplaceTrait(4, 5, 6)])
        self.assertEqual(Convert.json_to_action(json), expect)

    def test_validate_action_json_bad(self):
        json = 42
        with self.assertRaises(AssertionError):
            Convert.json_to_action(json)
        json = ["food!", [], [], [], []]
        with self.assertRaises(AssertionError):
            Convert.json_to_action(json)
        json = [3, [[2, 3, 4]], [], [], []]
        with self.assertRaises(AssertionError):
            Convert.json_to_action(json)
        json = [2, [], [[2]], [], []]
        with self.assertRaises(AssertionError):
            Convert.json_to_action(json)
        json = [2, [], [[2, 3]], [[2, -1]], []]
        with self.assertRaises(AssertionError):
            Convert.json_to_action(json)
        json = [2, [], [[2, 3]], [[2, -1]], [[1, 2, -1]]]
        with self.assertRaises(AssertionError):
            Convert.json_to_action(json)

    @classmethod
    def player_soft_eq(cls, player0, player1):
        return all([player0.name == player1.name,
                    player0.food_bag == player1.food_bag,
                    player0.hand == player1.hand,
                    cls.species_list_eq(player0.species, player1.species)])

    @classmethod
    def species_list_eq(cls, los0, los1):
        return (len(los0) == len(los1) and
                all(cls.species_soft_eq(spec0, spec1) for spec0, spec1 in zip(los0, los1)))

    @classmethod
    def species_soft_eq(cls, spec0, spec1):
        return all([spec0.population == spec1.population,
                    spec0.food == spec1.food,
                    spec0.body == spec1.body,
                    spec0.traits == spec1.traits,
                    spec0.fat_storage == spec1.fat_storage])


if __name__ == '__main__':
    unittest.main()
