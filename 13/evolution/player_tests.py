import copy
import unittest
import test_utils
from actions import *
from species import Species
from traitcard import TraitCard
from player import Player
from player_state import PlayerState
from choice import Choice


class TestPlayer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        test_utils.setup()

    def setUp(self):
        self.species_1 = Species(4, 4, 4)
        self.species_2 = Species(4, 4, 4)
        self.species_3 = Species(4, 4, 3)
        self.species_4 = Species(4, 3, 3)
        self.species_5 = Species(3, 1, 3)
        self.species_6 = Species(4, 3, 3)
        self.species_7 = Species(4, 4, 4)
        self.species_list = [self.species_2, self.species_4,
                             self.species_3, self.species_5,
                             self.species_1]
        self.player_1 = PlayerState(Player,
                                    species=[self.species_4,
                                             self.species_5,
                                             self.species_6])
        self.player_2 = PlayerState(Player,
                                    species=[self.species_1])
        self.player_3 = PlayerState(Player,
                                    species=[self.species_2,
                                             self.species_3,
                                             self.species_7])

        self.attacker = Species()
        self.attacker.traits = [TraitCard("carnivore")]
        self.defender = Species()

    def test_feed_fatty(self):
        self.species_4.traits = [TraitCard("fat-tissue")]
        self.species_1.traits = [TraitCard("fat-tissue")]
        self.species_5.traits = [TraitCard("fat-tissue")]
        self.assertEqual(Player.feed_fatty([self.species_4, self.species_1, self.species_5], 10),
                         [self.species_5, 3])
        self.assertEqual(Player.feed_fatty([self.species_4, self.species_1, self.species_5], 1),
                         [self.species_5, 1])
        self.assertEqual(Player.feed_fatty([self.species_4, self.species_1], 10),
                         [self.species_4, 3])

    def test_feed_herbivore(self):
        self.assertEqual(Player.feed_herbivores([self.species_4, self.species_5]), self.species_4)

    def give_carnivore_trait(self):
        self.player_1.species = [self.species_6, self.species_5, self.species_4]
        self.species_4.traits = ["carnivore"]
        self.species_5.traits = ["carnivore"]
        self.species_6.traits = ["carnivore"]

    def test_feed_carnivore_tie_attacker(self):
        # Test tie in largest carnivore in attacking player's hand => first species chosen
        self.give_carnivore_trait()
        self.player_1.species = [self.species_4, self.species_5, self.species_6]
        self.assertEqual(Player.feed_carnivore(self.player_1.species, self.player_1,
                                              [self.player_2, self.player_3]),
                                              [self.species_4, self.player_2, self.species_1])

    def test_feed_carnivore_ordering(self):
        # Repeat to test first is chosen again when order is changed
        self.give_carnivore_trait()
        self.assertEqual(Player.feed_carnivore(self.player_1.species, self.player_1,
                                              [self.player_2, self.player_3]),
                                              [self.species_6, self.player_2, self.species_1])

    def test_feed_carnivore_tie_defender(self):
        # Test tie in largest target between defending players' hands => first given player chosen
        self.give_carnivore_trait()
        self.assertEqual(Player.feed_carnivore(self.player_1.species, self.player_1,
                                              [self.player_3, self.player_2]),
                                              [self.species_6, self.player_3, self.species_2])

    def test_feed_carnivore_tie_largest(self):
        # Test tie in largest target within defending player's hand => first species chosen
        self.give_carnivore_trait()
        self.player_3.species = [self.species_7, self.species_3, self.species_2]
        self.assertEqual(Player.feed_carnivore(self.player_1.species, self.player_1,
                                              [self.player_3, self.player_2]),
                                              [self.species_6, self.player_3, self.species_7])

    def test_feed_carnivore_first_attackable(self):
        # Retest tie, but with first species unattackable => second largest chosen
        self.give_carnivore_trait()
        self.player_3.species = [self.species_7, self.species_3, self.species_2]
        self.species_7.traits = ["climbing"]
        self.assertEqual(Player.feed_carnivore(self.player_1.species, self.player_1,
                                              [self.player_3, self.player_2]),
                                              [self.species_6, self.player_3, self.species_2])

    def test_feed_carnivore_first_player_unattackable(self):
        # Repeat again, but since both largest in first player's hand are unattackable => second player w/ largest
        self.give_carnivore_trait()
        self.player_3.species = [self.species_7, self.species_3, self.species_2]
        self.species_7.traits = ["climbing"]
        self.species_2.traits = ["burrowing"]
        self.assertEqual(Player.feed_carnivore(self.player_1.species, self.player_1,
                                              [self.player_3, self.player_2]),
                                              [self.species_6, self.player_2, self.species_1])

    def test_feed_carnivore_smaller_attackable(self):
        # Test that if all largest species are unattackable, a smaller species is chosen
        self.give_carnivore_trait()
        self.player_3.species = [self.species_7, self.species_3, self.species_2]
        self.species_7.traits = ["climbing"]
        self.species_2.traits = ["burrowing"]
        self.species_1.traits = ["climbing"]
        self.assertEqual(Player.feed_carnivore(self.player_1.species, self.player_1,
                                              [self.player_3, self.player_2]),
                                              [self.species_6, self.player_3, self.species_3])

    def test_feed_carnivore_climbing(self):
        # Test that a carnivore with overriding traits attacks the largest species attackable
        self.give_carnivore_trait()
        self.player_3.species = [self.species_7, self.species_3, self.species_2]
        self.species_7.traits = ["climbing"]
        self.species_2.traits = ["burrowing"]
        self.species_1.traits = ["climbing"]
        self.species_3.traits = ["climbing"]
        self.species_4.traits.append("climbing")
        self.assertEqual(Player.feed_carnivore(self.player_1.species,
                                               self.player_1,
                                               [self.player_3, self.player_2]),
                         [self.species_4, self.player_3, self.species_7])

    def test_next_feeding(self):
        self.species_4.traits = ["carnivore"]
        self.species_5.traits = ["fat-tissue"]
        # Test if fat_tissue_species
        next_feeding = Player.next_feeding(self.player_1, 10, [self.player_2, self.player_3])
        self.assertEqual(next_feeding.species_index, 1)
        self.assertEqual(next_feeding.food_requested, 3)
        # Test if hungry_herbivores
        self.species_5.traits = []
        next_feeding = Player.next_feeding(self.player_1, 10, [self.player_2])
        self.assertEqual(next_feeding.species_index, 2)
        # Test if hungry_carnivore
        self.species_5.traits = ["carnivore"]
        self.species_6.traits = ["carnivore"]
        next_feeding = Player.next_feeding(self.player_1, 10, [self.player_2, self.player_3])
        self.assertEqual(next_feeding.attacker_index, 0)
        self.assertEqual(next_feeding.target_index, 0)
        self.assertEqual(next_feeding.defender_index, 0)
        # Test if you can attack your own species.
        next_feeding = Player.next_feeding(self.player_1, 10, [self.player_1])
        self.assertEqual(next_feeding.attacker_index, 0)
        self.assertEqual(next_feeding.target_index, 0)
        self.assertEqual(next_feeding.defender_index, 2)

    def test_is_larger(self):
        # Population different
        self.defender.population = 2
        self.attacker.population = 1
        self.assertEqual(Player.is_larger(self.defender, self.attacker), 1)
        self.assertEqual(Player.is_larger(self.attacker, self.defender), -1)
        # Same population different food
        self.attacker.population = 2
        self.defender.food = 2
        self.attacker.food = 1
        self.assertEqual(Player.is_larger(self.defender, self.attacker), 1)
        self.assertEqual(Player.is_larger(self.attacker, self.defender), -1)
        # Same population and food different body
        self.attacker.food = 2
        self.defender.body = 4
        self.attacker.body = 3
        self.assertEqual(Player.is_larger(self.defender, self.attacker), 1)
        self.assertEqual(Player.is_larger(self.attacker, self.defender), -1)
        # Equal population, food, and body
        self.attacker.body = 4
        self.assertEqual(Player.is_larger(self.defender, self.attacker), 0)

    def test_sort_lex(self):
        sorted_list = [self.species_2, self.species_1, self.species_3, self.species_4, self.species_5]
        self.assertEqual(Player.sort_lex(self.species_list), sorted_list)
        self.assertNotEqual(Player.sort_lex(self.species_list), self.species_list)

    def test_largest_tied_species(self):
        tied_species = [self.species_2, self.species_1]
        self.assertEqual(Player.largest_tied_species(self.species_list), tied_species)

    def test_largest_fatty_need(self):
        self.species_1.traits = [TraitCard("fat-tissue")]
        self.species_2.traits = [TraitCard("fat-tissue")]
        self.species_4.traits = [TraitCard("fat-tissue")]
        self.assertEqual(Player.largest_fatty_need([self.species_1, self.species_4]), self.species_4)
        self.assertEqual(Player.largest_fatty_need([self.species_1, self.species_2]), self.species_1)

    def test_choose(self):
        self.player_1.hand = [TraitCard("burrowing"), TraitCard("carnivore"), TraitCard("fertile")]
        expected = Action(0, [], [], [BoardAddition(1, [2])], [])
        choice = Choice(self.player_1, [self.species_list], [])
        self.assertEqual(expected, Player.choose(choice))

    def test_choose_gp(self):
        self.player_1.hand = [TraitCard("scavenger"), TraitCard("burrowing"),
                             TraitCard("carnivore"), TraitCard("fertile")]
        expected = Action(1, [PopGrow(3, 0)], [], [BoardAddition(2, [3])], [])
        choice = Choice(self.player_1, [self.species_list], [])
        actual = Player.choose(choice)
        self.assertEqual(expected, actual)

    def test_choose_gb(self):
        self.player_1.hand = [TraitCard("scavenger"), TraitCard("burrowing"),
                             TraitCard("carnivore"), TraitCard("fertile"), TraitCard("foraging")]
        expected = Action(1, [PopGrow(3, 4)], [BodyGrow(3, 0)], [BoardAddition(2, [3])], [])
        choice = Choice(self.player_1, [self.species_list], [])
        actual = Player.choose(choice)
        self.assertEqual(expected, actual)

    def test_choose_rt(self):
        self.player_1.hand = [TraitCard("long-neck"), TraitCard("scavenger"), TraitCard("burrowing"),
                             TraitCard("carnivore"), TraitCard("fertile"), TraitCard("foraging")]
        expected = Action(2, [PopGrow(3, 5)], [BodyGrow(3, 0)], [BoardAddition(3, [4])], [ReplaceTrait(3, 0, 1)])
        choice = Choice(self.player_1, [self.species_list], [])
        actual = Player.choose(choice)
        self.assertEqual(expected, actual)

    def test_choose_rt(self):
        self.player_1.hand = [TraitCard("long-neck"), TraitCard("scavenger"), TraitCard("burrowing"),
                             TraitCard("carnivore"), TraitCard("fertile"), TraitCard("foraging"), TraitCard("scavenger", 3)]
        expected = Action(2, [PopGrow(3, 5)], [BodyGrow(3, 0)], [BoardAddition(3, [4])], [ReplaceTrait(3, 0, 1)])
        choice = Choice(self.player_1, [self.species_list], [])
        actual = Player.choose(choice)
        player_expected = copy.deepcopy(self.player_1)
        player_expected.apply_action(expected)
        self.player_1.apply_action(actual)
        self.check_player(player_expected, self.player_1, {})

if __name__ == '__main__':
    unittest.main()
