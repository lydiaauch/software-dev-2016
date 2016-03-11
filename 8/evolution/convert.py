from species import Species
from traitcard import TraitCard
from player_state import PlayerState

class Convert(object):
    """
    Methods for converting between JSON input and Python objects
    """
    def __init__(self):
        pass

    @classmethod
    def configuration_to_dealer(cls, config):
        """
        Converts a Configuration json input into a dealer with the game as
        described in the Configuration object.
        :param config: A Configuration [LOP, Natural, LOC], where LOP is a
        list of 3 to 8 Players, the Natural represents food in the watering hole,
        and the LOC is the deck of cards in the order they will appear.
        :return: A Dealer with the game configured properly to the given config.
        """
        pass

    def validate_configuration_json(cls, config_json):
        return all([len(config_json) == 3,
                    config_json[1] > 0])

    @classmethod
    def json_to_player(cls, json_player):
        assert(cls.validate_player_json(json_player))
        name = json_player[0][1]
        food_bag = json_player[2][1]
        species = []
        hand = []

        for json_species in json_player[1][1]:
            species.append(cls.json_to_species(json_species))
        if len(json_player) == 4:
            for json_card in json_player[4][1]:
                hand.append(cls.json_to_trait_card(json_card))
        return PlayerState(name=name,
                           food_bag=food_bag,
                           species=species,
                           hand=hand)

    @classmethod
    def validate_player_json(cls, json_player):
        return all([len(json_player) == 3 or
                   (len(json_player) == 4 and
                        json_player[4][0] == "cards" and
                        len(json_player[4][1]) > 0),
                    json_player[0][0] == "id",
                    json_player[0][1] > 0,
                    json_player[1][0] == "species",
                    json_player[2][0] == "bag",
                    json_player[2][1] > 0])


    @classmethod
    def player_to_json(cls, player):
        assert(player.name >= 1 and player.food_bag >= 0)
        json_species = []
        for species_obj in player.species:
            json_species.append(cls.species_to_json(species_obj))
        return [["id", player.name], ["species", json_species], ["bag", player.food_bag]]


    @classmethod
    def json_to_species(cls, json_species):
        assert(cls.validate_species_json(json_species))
        species_food = json_species[0][1]
        species_body = json_species[1][1]
        species_pop = json_species[2][1]
        species_traits = []
        for trait in json_species[3][1]:
            species_traits.append(cls.json_to_trait(trait))
        species_obj = Species(species_pop, species_food, species_body, species_traits)
        if len(json_species) == 5:
            species_obj.fat_storage = json_species[4][1]
        return species_obj

    @classmethod
    def validate_species_json(cls, json_species):
        return all([len(json_species) == 4 or
                    (len(json_species) == 5 and
                        json_species[4][0] == "fat-food" and
                        json_species[4][1] > 0),
                    json_species[0][0] == "food",
                    json_species[0][1] >= 0,
                    json_species[1][0] == "body",
                    json_species[1][1] >= 0,
                    json_species[2][0] == "population",
                    json_species[2][1] >  0,
                    json_species[3][0] == "traits"])

    @classmethod
    def species_to_json(cls, species_obj):
        assert(all([species_obj.population >= 1, species_obj.food >= 0, species_obj.body >= 0]))
        json_traits = []
        for trait in species_obj.traits:
            json_traits.append(cls.trait_to_json(trait))
        json_species = [["food", species_obj.food], ["body", species_obj.body],
                        ["population", species_obj.population], ["traits", json_traits]]
        if species_obj.fat_storage is not None and species_obj.fat_storage > 0:
            json_species.append(["fat-food", species_obj.fat_storage])
        return json_species

    @classmethod
    def json_to_trait(cls, json_trait):
        return TraitCard(json_trait)

    @classmethod
    def trait_to_json(cls, trait_card):
        return trait_card.trait