import unittest
from species import Species
from traitcard import TraitCard
from player_state import PlayerState
from convert import Convert


class TestConvert(unittest.TestCase):

    def setUp(self):
        self.jt_1 = "carnivore"
        self.jt_2 = "fat-tissue"
        self.jt_3 = "burrowing"
        self.jt_4 = "climbing"

        self.jSpecies_1 = [["food", 2], ["body", 2], ["population", 2], ["traits", [self.jt_1]]]
        self.jSpecies_2 = [["food", 2], ["body", 3], ["population", 3], ["traits", [self.jt_2]]]
        self.jSpecies_3 = [["food", 2], ["body", 3], ["population", 4], ["traits", [self.jt_3, self.jt_4]]]
        self.jSpecies_4 = [["food", 2], ["body", 2], ["population", 2], ["traits", [self.jt_3, self.jt_4]]]

        self.jPlayer_1 = [["id", 1], ["species", [self.jSpecies_1]], ["bag", 2]]
        self.jPlayer_2 = [["id", 2], ["species", [self.jSpecies_2]], ["bag", 1]]
        self.jPlayer_3 = [["id", 3], ["species", [self.jSpecies_3, self.jSpecies_4]], ["bag", 3]]

        self.json_feeding = [self.jPlayer_1, 10, [self.jPlayer_2, self.jPlayer_3]]
        self.json_feed_1 = False
        self.json_feed_2 = self.jSpecies_3
        self.json_feed_3 = [self.jSpecies_2, 3]
        self.json_feed_4 = [self.jSpecies_1, self.jPlayer_2, self.jSpecies_2]

        self.t_1 = TraitCard("carnivore")
        self.t_2 = TraitCard("fat-tissue")
        self.t_3 = TraitCard("burrowing")
        self.t_4 = TraitCard("climbing")

        self.species_1 = Species(2, 2, 2, [self.t_1])
        self.species_2 = Species(3, 2, 3, [self.t_2], 0)
        self.species_3 = Species(4, 2, 3, [self.t_3, self.t_4])
        self.species_4 = Species(2, 2, 2, [self.t_3, self.t_4])

        self.player_1 = PlayerState(name=1, food_bag=2, species=[self.species_1])
        self.player_2 = PlayerState(name=2, food_bag=1, species=[self.species_2])
        self.player_3 = PlayerState(name=3, food_bag=3, species=[self.species_3, self.species_4])

        self.feeding = [self.player_1, 10, [self.player_2, self.player_3]]
        self.feed_1 = False
        self.feed_2 = self.species_3
        self.feed_3 = [self.species_2, 3]
        self.feed_4 = [self.species_1, self.player_2, self.species_2]

    def test_json_to_trait(self):
        self.assertEqual(Convert.json_to_trait(self.jt_1), self.t_1)
        self.assertNotEqual(Convert.json_to_trait(self.jt_1), self.t_2)

    def test_trait_to_json(self):
        self.assertEqual(Convert.trait_to_json(self.t_1), self.jt_1)
        self.assertNotEqual(Convert.trait_to_json(self.t_1), self.jt_2)

    def test_json_to_species(self):
        self.assertEqual(Convert.json_to_species(self.jSpecies_1), self.species_1)
        self.assertEqual(Convert.json_to_species(self.jSpecies_2), self.species_2)
        self.assertNotEqual(Convert.json_to_species(self.jSpecies_1), self.species_2)
        self.jSpecies_1[0][1] = -1
        self.assertRaises(AssertionError, Convert.json_to_species, self.jSpecies_1)

    def test_species_to_json(self):
        self.assertEqual(Convert.species_to_json(self.species_1), self.jSpecies_1)
        self.assertNotEqual(Convert.species_to_json(self.species_1), self.jSpecies_2)
        self.species_1.population = -1
        self.assertRaises(AssertionError, Convert.species_to_json, self.species_1)

    def test_json_to_player(self):
        self.assertEqual(Convert.json_to_player(self.jPlayer_1), self.player_1)
        self.assertNotEqual(Convert.json_to_player(self.jPlayer_1), self.player_2)
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

    def test_bad_json_to_player(self):
        bad_json = [["foood", 2], ["body", 2], ["population", 2], ["traits", [self.jt_1]]]
        self.assertRaises(Exception, Convert.json_to_player, bad_json)


if __name__ == '__main__':
    unittest.main()
