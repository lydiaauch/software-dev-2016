import unittest
from helpers import *
from species import Species
from player_state import PlayerState


class TestHelpers(unittest.TestCase):
    def setUp(self):
        self.species_0 = Species(4, 4, 4)
        self.species_1 = Species(4, 4, 4)
        self.player_0 = PlayerState(None, species=[self.species_0])
        self.player_1 = PlayerState(None, species=[self.species_1])

    def test_carnivore_targets(self):
        self.species_0.traits = ["carnivore"]
        self.assertEqual(carnivore_targets(self.species_0, [self.player_1]),
                         [self.species_1])

        self.species_1.traits = ["climbing"]
        # self.assertEqual(carnivore_targets(self.species_0, list_of_opponents), [])

    def test_is_unique_list(self):
        self.assertTrue(is_unique_list([1, 2, 3]))
        self.assertTrue(is_unique_list([1]))
        self.assertTrue(is_unique_list([]))
        self.assertFalse(is_unique_list([1, 1]))
        self.assertFalse(is_unique_list([1, 0, 1]))

if __name__ == '__main__':
    unittest.main()
