import unittest
from species import Species
from traitcard import TraitCard


class TestSpecies(unittest.TestCase):

    def setUp(self):
        self.attacker = Species()
        self.attacker.traits = [TraitCard("carnivore")]
        self.defender = Species()
        self.left_neighbor = Species()
        self.right_neighbor = Species()

        self.species_1 = Species(4, 4, 4)
        self.species_2 = Species(4, 4, 4)
        self.species_3 = Species(4, 4, 3)
        self.species_4 = Species(4, 3, 3)
        self.species_5 = Species(3, 3, 3)
        self.species_list = [self.species_2, self.species_4, self.species_3, self.species_5, self.species_1]


    def test_trait_names(self):
        self.assertEqual(self.defender.trait_names(), [])
        self.assertEqual(self.attacker.trait_names(), ["carnivore"])

    def test_attackable(self):
        self.assertTrue(self.defender.is_attackable(self.attacker))

    def test_no_carnivore(self):
        self.attacker.traits = []
        self.assertFalse(self.defender.is_attackable(self.attacker))

    def test_burrowing(self):
        self.defender.traits = [TraitCard("burrowing")]
        self.defender.population, self.defender.food = (4, 4)
        self.assertFalse(self.defender.is_attackable(self.attacker))
        self.defender.food = 3
        self.assertTrue(self.defender.is_attackable(self.attacker))

    def test_climbing(self):
        self.defender.traits = [TraitCard("climbing")]
        self.assertFalse(self.defender.is_attackable(self.attacker))
        self.attacker.traits.append(TraitCard("climbing"))
        self.assertTrue(self.defender.is_attackable(self.attacker))

    def test_hard_shell(self):
        self.defender.traits = [TraitCard("hard-shell")]
        self.defender.body = 3
        self.attacker.body = 6
        self.assertFalse(self.defender.is_attackable(self.attacker))
        self.attacker.body = 7
        self.assertTrue(self.defender.is_attackable(self.attacker))

    def test_herding(self):
        self.defender.traits = [TraitCard("herding")]
        self.defender.population = 4
        self.attacker.population = 3
        self.assertFalse(self.defender.is_attackable(self.attacker))
        self.attacker.population = 5
        self.assertTrue(self.defender.is_attackable(self.attacker))

    def test_symbiosis(self):
        self.defender.traits = [TraitCard("symbiosis")]
        self.defender.body = 3
        self.right_neighbor.body = 5
        self.assertFalse(self.defender.is_attackable(self.attacker, right_neighbor=self.right_neighbor))
        self.right_neighbor.body = 2
        self.assertTrue(self.defender.is_attackable(self.attacker, right_neighbor=self.right_neighbor))

    def test_warning_call(self):
        self.left_neighbor.traits = [TraitCard("warning-call")]
        self.right_neighbor.traits = [TraitCard("warning-call")]
        self.assertFalse(self.defender.is_attackable(self.attacker, left_neighbor=self.left_neighbor))
        self.assertFalse(self.defender.is_attackable(self.attacker, right_neighbor=self.right_neighbor))
        self.attacker.traits.append(TraitCard("ambush"))
        self.assertTrue(self.defender.is_attackable(self.attacker, left_neighbor=self.left_neighbor))

    def test_is_larger(self):
        # Population different
        self.defender.population = 2
        self.attacker.population = 1
        self.assertEqual(Species.is_larger(self.defender, self.attacker), 1)
        self.assertEqual(Species.is_larger(self.attacker, self.defender), -1)
        # Same population different food
        self.attacker.population = 2
        self.defender.food = 2
        self.attacker.food = 1
        self.assertEqual(Species.is_larger(self.defender, self.attacker), 1)
        self.assertEqual(Species.is_larger(self.attacker, self.defender), -1)
        # Same population and food different body
        self.attacker.food = 2
        self.defender.body = 4
        self.attacker.body = 3
        self.assertEqual(Species.is_larger(self.defender, self.attacker), 1)
        self.assertEqual(Species.is_larger(self.attacker, self.defender), -1)
        # Equal population, food, and body
        self.attacker.body = 4
        self.assertEqual(Species.is_larger(self.defender, self.attacker), 0)

    def test_sort_lex(self):
        sorted_list = [self.species_2, self.species_1, self.species_3, self.species_4, self.species_5]
        self.assertEqual(Species.sort_lex(self.species_list), sorted_list)
        self.assertNotEqual(Species.sort_lex(self.species_list), self.species_list)

    def test_largest_tied_species(self):
        tied_species = [self.species_2, self.species_1]
        self.assertEqual(Species.largest_tied_species(self.species_list), tied_species)

    def test_largest_fatty_need(self):
        self.species_1.traits = [TraitCard("fat-tissue")]
        self.species_2.traits = [TraitCard("fat-tissue")]
        self.species_4.traits = [TraitCard("fat-tissue")]
        self.assertEqual(Species.largest_fatty_need([self.species_1, self.species_4]), self.species_4)
        self.assertEqual(Species.largest_fatty_need([self.species_1, self.species_2]), self.species_1)

if __name__ == '__main__':
    unittest.main()


