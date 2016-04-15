import copy
import unittest
import test_utils
from species import Species
from traitcard import TraitCard
from player_state import PlayerState
from actions import *
from player import Player


class TestPlayerState(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        test_utils.setup()

    def setUp(self):
        species_0 = Species(population=1,
                            food=3,
                            body=4,
                            traits=["carnivore"])

        species_1 = Species(population=1,
                            food=1,
                            body=1,
                            traits=["burrowing"])

        species_2 = Species(population=1,
                            food=0,
                            body=1,
                            traits=["fat-tissue"])

        species = [species_0, species_1, species_2]

        hand = [TraitCard("long-neck", food_points=2),
                TraitCard("climbing", food_points=-2),
                TraitCard("scavenger", food_points=4)]
        self.player = PlayerState(Player, hand=hand, species=species)

    def test_create_new_boards_one(self):
        board_addition = BoardAddition(0, traits=[1, 2])
        before = copy.deepcopy(self.player)
        self.player.create_new_boards([board_addition])
        self.player.remove_used_cards()

        changes = {
            "species": {3: {
                "population": 1,
                "food": 0,
                "body": 0,
                "fat_storage": 0,
                "traits": ["climbing", "scavenger"]}},
            "hand": []}
        self.check_player(before, self.player, changes)

    def test_create_new_boards_many(self):
        board_addition_0 = BoardAddition(0)
        board_addition_1 = BoardAddition(1)
        board_addition_2 = BoardAddition(2)
        before = copy.deepcopy(self.player)
        self.player.create_new_boards([board_addition_0,
                                       board_addition_1,
                                       board_addition_2])
        self.player.remove_used_cards()
        new_species = {
            "population": 1,
            "food": 0,
            "body": 0,
            "fat_storage": 0,
            "traits": []
        }

        changes = {
            "species": {
                3: new_species,
                4: new_species,
                5: new_species,
            },
            "hand": []
        }
        self.check_player(before, self.player, changes)

    # TODO: Species don't need whole trait cards, just their traits.
    def test_replace_traits_one(self):
        replacements = [ReplaceTrait(0, 0, 0)]
        before = copy.deepcopy(self.player)
        self.player.replace_traits(replacements)
        self.player.remove_used_cards()
        changes = {
            "species":
                {0: {"traits": ["long-neck"]}},
            "hand":
                [TraitCard("climbing", food_points=-2),
                 TraitCard("scavenger", food_points=4)]
        }
        self.check_player(before, self.player, changes)

    def test_replace_traits_many(self):
        replacements = [ReplaceTrait(0, 0, 0),
                        ReplaceTrait(2, 0, 1),
                        ReplaceTrait(1, 0, 2)]
        before = copy.deepcopy(self.player)
        self.player.replace_traits(replacements)
        self.player.remove_used_cards()
        changes = {
            "species":
                {0: {"traits": ["long-neck"]},
                 2: {"traits": ["climbing"]},
                 1: {"traits": ["scavenger"]}},
            "hand":
                []
        }
        self.check_player(before, self.player, changes)

    def test_increase_populations_one(self):
        pop_grows = [PopGrow(1, 1)]
        before = copy.deepcopy(self.player)
        self.player.increase_populations(pop_grows)
        self.player.remove_used_cards()
        changes = {
            "species":
                {1: {"population": 2}},
            "hand":
                [TraitCard("long-neck", food_points=2),
                 TraitCard("scavenger", food_points=4)]
        }
        self.check_player(before, self.player, changes)

    def test_increase_populations_many_same_species(self):
        pop_grows = [PopGrow(1, 1), PopGrow(1, 0), PopGrow(1, 2)]
        before = copy.deepcopy(self.player)
        self.player.increase_populations(pop_grows)
        self.player.remove_used_cards()
        changes = {
            "species":
                {1: {"population": 4}},
            "hand":
                []
        }
        self.check_player(before, self.player, changes)

    def test_increase_populations_many_different_species(self):
        pop_grows = [PopGrow(1, 1), PopGrow(0, 0), PopGrow(2, 2)]
        before = copy.deepcopy(self.player)
        self.player.increase_populations(pop_grows)
        self.player.remove_used_cards()
        changes = {
            "species":
                {0: {"population": 2},
                 1: {"population": 2},
                 2: {"population": 2}},
            "hand":
                []
        }
        self.check_player(before, self.player, changes)

    def test_increase_body_sizes_one(self):
        body_grows = [BodyGrow(1, 1)]
        before = copy.deepcopy(self.player)
        self.player.increase_body_sizes(body_grows)
        self.player.remove_used_cards()
        changes = {
            "species":
                {1: {"body": 2}},
            "hand":
                [TraitCard("long-neck", food_points=2),
                 TraitCard("scavenger", food_points=4)]
        }
        self.check_player(before, self.player, changes)

    def test_increase_body_sizes_many_same_species(self):
        body_grows = [BodyGrow(1, 1), BodyGrow(1, 0), BodyGrow(1, 2)]
        before = copy.deepcopy(self.player)
        self.player.increase_body_sizes(body_grows)
        self.player.remove_used_cards()
        changes = {
            "species": {1: {"body": 4}},
            "hand": []
        }
        self.check_player(before, self.player, changes)

    def test_increase_body_sizes_many_different_species(self):
        body_grows = [BodyGrow(1, 1), BodyGrow(0, 0), BodyGrow(2, 2)]
        before = copy.deepcopy(self.player)
        self.player.increase_body_sizes(body_grows)
        self.player.remove_used_cards()
        changes = {
            "species":
                {0: {"body": 5},
                 1: {"body": 2},
                 2: {"body": 2}},
            "hand":
                []
        }
        self.check_player(before, self.player, changes)

    def test_can_feed(self):
        self.assertTrue(self.player.can_feed([self.player]))
        self.player.species[0].traits = ["carnivore"]
        self.player.species[1].traits = ["carnivore"]
        self.player.species[2].traits = ["carnivore"]
        self.assertFalse(self.player.can_feed([]))


if __name__ == '__main__':
    unittest.main()
