import unittest
from dealer import *
from species import Species
from traitcard import TraitCard
from player import Player

class TestDealer(unittest.TestCase):
    def setUp(self):
        self.dealer = Dealer([Player(), Player(), Player(), Player()])
        self.dealer.watering_hole = 10
        self.dealer.list_of_player_sets[0]['state'].name = 0;
        self.dealer.list_of_player_sets[1]['state'].name = 1;
        self.dealer.list_of_player_sets[2]['state'].name = 2;
        self.dealer.list_of_player_sets[3]['state'].name = 3;
        self.dealer.current_player_index = 2

        self.species_1 = Species(4, 4, 4)
        self.species_2 = Species(4, 4, 4)
        self.species_3 = Species(4, 4, 3)
        self.species_4 = Species(4, 3, 3)
        self.species_5 = Species(3, 3, 3)
        self.species_list = [self.species_1,
                             self.species_2,
                             self.species_3,
                             self.species_4,
                             self.species_5]

        self.dealer.list_of_player_sets[0]['state'].species = [self.species_1]
        self.dealer.list_of_player_sets[1]['state'].species = [self.species_2]
        self.dealer.list_of_player_sets[2]['state'].species = [self.species_3]
        self.dealer.list_of_player_sets[3]['state'].species = [self.species_4, self.species_5]

    def test_check_for_hungries(self):
        hungries = self.dealer.check_for_hungries(self.species_list)
        self.assertEqual(1, len(hungries))
        self.assertEqual(self.species_4, hungries[0])

    def test_opponents(self):
        opponents = self.dealer.opponents()
        self.assertEqual(3, len(opponents))

        opponents_name_2 = filter(lambda p: p.name == 2, opponents)
        self.assertEqual(0, len(opponents_name_2))

    def test_carnivore_targets(self):
        list_of_player = self.dealer.make_list_of_player_states()
        self.species_3.traits = [TraitCard("carnivore")]
        self.species_2.traits = [TraitCard("climbing")]
        self.species_4.traits = [TraitCard("climbing")]
        self.species_5.traits = [TraitCard("climbing")]

        self.assertEqual(Dealer.carnivore_targets(self.species_3, list_of_player), [self.species_1])

        self.species_1.traits = [TraitCard("climbing")]
        self.assertEqual(Dealer.carnivore_targets(self.species_3, list_of_player), None)

    def test_auto_eat(self):
        self.dealer.current_player_index = 2
        self.species_3.traits= [TraitCard("fat-tissue")]
        self.species_3.fat_storage = 0
        self.assertEqual(self.dealer.auto_eat(), [self.species_3, 3])

        self.species_3.traits = []
        self.species_3.food = 2
        self.assertEqual(self.dealer.auto_eat(), self.species_3)

        self.species_3.traits = [TraitCard("carnivore")]
        self.assertIsNone(self.dealer.auto_eat())

        self.species_2.traits = [TraitCard("climbing")]
        self.species_4.traits = [TraitCard("climbing")]
        self.species_5.traits = [TraitCard("climbing")]

        self.assertEqual(self.dealer.auto_eat(),
                         [self.species_3,
                          self.dealer.list_of_player_sets[2]['state'],
                          self.species_1])

        self.species_3.food = 4
        self.assertIsNone(self.dealer.auto_eat())


if __name__ == '__main__':
    unittest.main()
