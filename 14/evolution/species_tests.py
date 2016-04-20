from species import Species
import unittest


class TestSpecies(unittest.TestCase):

    def setUp(self):
        self.attacker = Species()
        self.attacker.traits = ["carnivore"]
        self.defender = Species()
        self.left_neighbor = Species()
        self.right_neighbor = Species()

        self.species_1 = Species(4, 4, 4)
        self.species_2 = Species(4, 4, 4)
        self.species_3 = Species(4, 4, 3)
        self.species_4 = Species(4, 3, 3)
        self.species_5 = Species(3, 3, 3)
        self.species_list = [self.species_2, self.species_4,
                             self.species_3, self.species_5, self.species_1]

    def test_can_eat(self):
        self.assertFalse(self.species_1.can_eat())
        self.assertTrue(self.species_4.can_eat())
        fat_tissue = Species(4, 3, 4, ["fat-tissue"], 3)
        self.assertTrue(fat_tissue.can_eat())
        fat_tissue.fat_storage = 4
        self.assertTrue(fat_tissue.can_eat())
        fat_tissue.food = 4
        self.assertFalse(fat_tissue.can_eat())

    def test_trait_names(self):
        self.assertEqual(self.defender.traits, [])
        self.assertEqual(self.attacker.traits, ["carnivore"])

    def test_attackable(self):
        self.assertTrue(self.defender.is_attackable(self.attacker))

    def test_no_carnivore(self):
        self.attacker.traits = []
        self.assertFalse(self.defender.is_attackable(self.attacker))

    def test_burrowing(self):
        self.defender.traits = ["burrowing"]
        self.defender.population, self.defender.food = (4, 4)
        self.assertFalse(self.defender.is_attackable(self.attacker))
        self.defender.food = 3
        self.assertTrue(self.defender.is_attackable(self.attacker))

    def test_climbing(self):
        self.defender.traits = ["climbing"]
        self.assertFalse(self.defender.is_attackable(self.attacker))
        self.attacker.traits.append("climbing")
        self.assertTrue(self.defender.is_attackable(self.attacker))

    def test_hard_shell(self):
        self.defender.traits = ["hard-shell"]
        self.defender.body = 3
        self.attacker.body = 6
        self.assertFalse(self.defender.is_attackable(self.attacker))
        self.attacker.body = 7
        self.assertTrue(self.defender.is_attackable(self.attacker))

    def test_herding(self):
        self.defender.traits = ["herding"]
        self.defender.population = 4
        self.attacker.population = 3
        self.assertFalse(self.defender.is_attackable(self.attacker))
        self.attacker.population = 5
        self.assertTrue(self.defender.is_attackable(self.attacker))

    def test_symbiosis(self):
        self.defender.traits = ["symbiosis"]
        self.defender.body = 3
        self.right_neighbor.body = 5
        self.assertFalse(self.defender.is_attackable(self.attacker,
                                                     right_neighbor=self.right_neighbor))
        self.right_neighbor.body = 2
        self.assertTrue(self.defender.is_attackable(self.attacker,
                                                    right_neighbor=self.right_neighbor))

    def test_warning_call(self):
        self.left_neighbor.traits = ["warning-call"]
        self.right_neighbor.traits = ["warning-call"]
        self.assertFalse(self.defender.is_attackable(self.attacker,
                                                     left_neighbor=self.left_neighbor))
        self.assertFalse(self.defender.is_attackable(self.attacker,
                                                     right_neighbor=self.right_neighbor))
        self.attacker.traits.append("ambush")
        self.assertTrue(self.defender.is_attackable(self.attacker,
                                                    left_neighbor=self.left_neighbor))


if __name__ == '__main__':
    unittest.main()
