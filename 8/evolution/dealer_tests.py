import unittest
from dealer import *
from species import Species
from traitcard import TraitCard
from player import Player

class TestDealer(unittest.TestCase):
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
        self.species_list = [self.species_1,
                             self.species_2,
                             self.species_3,
                             self.species_4,
                             self.species_5]

        self.dealer.player_sets[0]['state'].species = [self.species_1]
        self.dealer.player_sets[1]['state'].species = [self.species_2]
        self.dealer.player_sets[2]['state'].species = [self.species_3]
        self.dealer.player_sets[3]['state'].species = [self.species_4, self.species_5]


    def test_check_for_hungries(self):
        hungries = self.dealer.check_for_hungries(self.species_list)
        self.assertEqual(2, len(hungries))
        self.assertEqual(self.species_4, hungries[0])

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

    def test_auto_eat(self):
        self.dealer.current_player_index = 2
        self.species_3.traits= [TraitCard("fat-tissue")]
        self.species_3.fat_storage = 0
        self.assertEqual(self.dealer.auto_eat(), [0, 3])

        self.species_3.traits = []
        self.species_3.food = 2
        self.assertEqual(self.dealer.auto_eat(), 0)

        self.species_3.traits = [TraitCard("carnivore")]
        self.assertIsNone(self.dealer.auto_eat())

        self.species_2.traits = [TraitCard("climbing")]
        self.species_4.traits = [TraitCard("climbing")]
        self.species_5.traits = [TraitCard("climbing")]

        self.assertEqual(self.dealer.auto_eat(), [0, 0, 0])

        self.species_3.food = 4
        self.assertIsNone(self.dealer.auto_eat())

    def test_feed_1_herbivore(self):
        # current player has single hungry herbivore -> auto_eat
        self.dealer.feed1()
        self.assertEqual(self.dealer.watering_hole, 9)
        self.assertEqual(self.dealer.current_player_index, 3)
        self.assertEqual(self.species_3.food, 4)

    def test_feed_1_fatty(self):
        # current player is feeding fat-tissue species
        self.species_3.traits = [TraitCard("fat-tissue")]
        self.dealer.feed1()
        self.assertEqual(self.dealer.watering_hole, 7)
        self.assertEqual(self.dealer.current_player_index, 3)
        self.assertEqual(self.species_3.food, 3)
        self.assertEqual(self.species_3.fat_storage, 3)

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
        with self.assertRaises(Exception):
            self.dealer.feed1()

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
