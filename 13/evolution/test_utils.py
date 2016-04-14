import unittest
from dealer import *
from species import Species
from traitcard import TraitCard
from player import Player


def setup():
    unittest.TestCase.check_dealer = check_dealer
    unittest.TestCase.check_player = check_player
    unittest.TestCase.check_species = check_species
    unittest.TestCase.check_attribute = check_attribute


def check_dealer(self, before, after, changes):
    """
    Checks that all aspects of self.dealer are the same except for the changes
    specified in the changes after calling dealer.method. changes is a subset of
    {
        "watering_hole": Number,
        "current_player_index": Number,
        "deck": [TraitCard, ...]
        "players": {Number: PlayerChanges, ...} where a PlayerChanges is a dict
                                                describing the changes to the
                                                player state at the given index
    }
    #TODO: index players by id.
    """
    self.check_attribute(before, after, changes, "watering_hole")
    self.check_attribute(before, after, changes, "current_player_index")
    self.check_attribute(before, after, changes, "deck")
    for i in range(len(before.players)):
        if "players" in changes and i in changes["players"]:
            self.check_player(before.players[i],
                              after.players[i],
                              changes["players"][i])
        else:
            self.check_player(before.players[i],
                              after.players[i],
                              {})


def check_player(self, before, after, changes):
    """
    Checks that all aspects of the given player are the same except for changes
    specified in the configuration. A changes is a subset of the dictionary
    {
        "name": Any,
        "food_bag": Number,
        "hand": [TraitCard, ...],
        "species": {Number: SpeciesChanges, ...} where a SpeciesChanges is a
                                                 dict describing the changes
                                                 to species at the given index,
                                                 or is the string "Extinct"
                                                 if the species at that index
                                                 went extinct.
    }
    """
    self.check_attribute(before, after, changes, "name")
    self.check_attribute(before, after, changes, "food_bag")
    self.check_attribute(before, after, changes, "hand")
    i = 0  # before.species list index
    j = 0  # after.species  list index
    while i < len(before.species) or j < len(after.species):
        if "species" in changes and i in changes["species"]:
            if changes["species"][i] == "Extinct":
                i += 1
                continue
            elif i < len(before.species):
                self.check_species(before.species[i],
                                   after.species[j],
                                   changes["species"][i])
            else:
                self.check_species(None, after.species[j], changes["species"][i])
        else:
            self.assertTrue(i < len(before.species) and
                            j < len(after.species))
            self.check_species(before.species[i], after.species[j], {})

        i += 1
        j += 1


def check_species(self, before, after, changes):
    """
    Checks that all aspects of the given species are the same except for changes
    specified in the configuration. A changes is a subset of the dictionary
    {
        "population": Number,
        "food": Number,
        "body": Number,
        "fat_storage": Number,
        "traits": [String, ...]
    }
    """
    self.check_attribute(before, after, changes, "population")
    self.check_attribute(before, after, changes, "food")
    self.check_attribute(before, after, changes, "body")
    self.check_attribute(before, after, changes, "fat_storage")
    self.check_attribute(before, after, changes, "traits")

def check_attribute(self, before, after, changes, attribute):
    """
    Checks if a given attribute has changed from the before to after objects.
    :param before: The object to check before the changes applied.
    :param after: The object to check after the changes applied.
    :param changes: Dictionary where the keys are the names of the attributes
    that should have changed and the values are the expected values.
    :param attribute: The string name of the attribute to check.
    """
    if attribute in changes:
        self.assertEqual(getattr(after, attribute), changes[attribute])
    else:
        self.assertEqual(getattr(after, attribute), getattr(before, attribute))
