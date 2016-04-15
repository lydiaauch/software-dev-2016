from species import Species
from traitcard import TraitCard
from player_state import PlayerState
from player import Player
from dealer import Dealer
from actions import *
from choice import Choice


class Convert(object):
    """
    Methods for converting between JSON input and Python objects
    """
    def __init__(self):
        pass

    @classmethod
    def json_to_dealer(cls, json_config):
        """
        Converts a Configuration json input into a dealer with the game as
        described in the Configuration object.
        :param json_config: A Configuration [LOP, Natural, LOC], where LOP is a
        list of Players, the Natural represents food in the watering hole,
        and the LOC is the deck of cards in the order they will appear.
        :return: A Dealer with the game configured to the given json_config.
        """
        assert(cls.validate_configuration_json(json_config))
        players_interfaces = []
        num_players = len(json_config[0])
        for i in range(num_players):
            players_interfaces.append(Player())
        dealer = Dealer(players_interfaces)
        for i in range(num_players):
            dealer.players[i] = cls.json_to_player(json_config[0][i])
        dealer.watering_hole = json_config[1]
        deck = []
        for i in range(len(json_config[2])):
            deck.append(cls.json_to_trait_card(json_config[2][i]))
        dealer.deck = deck
        return dealer

    @classmethod
    def dealer_to_json(cls, dealer):
        config_json = []
        player_json = []
        for player in dealer.players:
            player_json.append(Convert.player_to_json(player))
        config_json.append(player_json)
        config_json.append(dealer.watering_hole)
        deck_json = []
        for card in dealer.deck:
            deck_json.append(Convert.trait_card_to_json(card))
        config_json.append(deck_json)
        return config_json

    @classmethod
    def validate_configuration_json(cls, config_json):
        return all([len(config_json) == 3,
                    len(config_json[0]) <= 8,
                    len(config_json[0]) >= 3,
                    config_json[1] >= 0])

    @classmethod
    def json_to_choice(cls, json_choice):
        assert(cls.validate_choice_json(json_choice))
        player = cls.json_to_player(json_choice[0])
        before = cls.json_to_listof_species(json_choice[1])
        after = cls.json_to_listof_species(json_choice[2])
        return Choice(player, before, after)

    @classmethod
    def json_to_listof_species(cls, json_species_list):
        return map(lambda los: map(lambda spec: cls.json_to_species(spec), los), json_species_list)

    @classmethod
    def validate_choice_json(cls, json_choice):
        # TODO
        return True

    @classmethod
    def list_of_species_to_json(cls, los):
        return map(los, lambda spec: species_to_json(spec))

    @classmethod
    def json_to_player_state(cls, json_player):
        # [Natural,[Species+, ..., Species+], Cards]
        assert(cls.validate_player_state_json(json_player))
        species = cls.json_to_listof_species(json_player[1])
        cards = map(lambda c: cls.json_to_trait_card(c), json_player[2])
        return PlayerState(None, name=None, food_bag=json_player[0], hand=cards, species=species)

    @classmethod
    def validate_player_state_json(cls, json_player):
        # TODO
        return True

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
            for json_card in json_player[3][1]:
                hand.append(cls.json_to_trait_card(json_card))
        return PlayerState(Player,
                           name=name,
                           food_bag=food_bag,
                           species=species,
                           hand=hand)

    @classmethod
    def validate_player_json(cls, json_player):
        return all([len(json_player) == 3 or
                   (len(json_player) == 4 and
                        json_player[3][0] == "cards" and
                        len(json_player[3][1]) >= 0),
                    json_player[0][0] == "id",
                    json_player[0][1] > 0,
                    json_player[1][0] == "species",
                    json_player[2][0] == "bag",
                    json_player[2][1] >= 0])

    @classmethod
    def player_to_json(cls, player):
        assert(player.name >= 1 and player.food_bag >= 0)
        json_species = []
        for species_obj in player.species:
            json_species.append(cls.species_to_json(species_obj))
        json = [["id", player.name], ["species", json_species], ["bag", player.food_bag]]
        if len(player.hand) != 0:
            json_cards = []
            for card in player.hand:
                json_cards.append(cls.trait_card_to_json(card))
            json.append(["cards", json_cards])
        return json

    @classmethod
    def json_to_species(cls, json_species):
        assert(cls.validate_species_json(json_species))
        species_food = json_species[0][1]
        species_body = json_species[1][1]
        species_pop = json_species[2][1]
        species_traits = []
        for trait in json_species[3][1]:
            species_traits.append(trait)
        species_obj = Species(species_pop, species_food, species_body, species_traits)
        if len(json_species) == 5:
            species_obj.fat_storage = json_species[4][1]
        return species_obj

    @classmethod
    def validate_species_json(cls, json_species):
        return all([len(json_species) == 4 or
                    (len(json_species) == 5 and
                        json_species[4][0] == "fat-food" and
                        json_species[4][1] >= 0),
                    json_species[0][0] == "food",
                    json_species[0][1] >= 0,
                    json_species[1][0] == "body",
                    json_species[1][1] >= 0,
                    json_species[2][0] == "population",
                    json_species[2][1] > 0,
                    json_species[3][0] == "traits"])

    @classmethod
    def species_to_json(cls, species_obj):
        assert(all([species_obj.population >= 1, species_obj.food >= 0, species_obj.body >= 0]))
        json_species = [["food", species_obj.food], ["body", species_obj.body],
                        ["population", species_obj.population], ["traits", species_obj.traits]]
        if species_obj.fat_storage is not None and species_obj.fat_storage > 0:
            json_species.append(["fat-food", species_obj.fat_storage])
        return json_species

    @classmethod
    def json_to_actions(cls, json_step4):
        actions = []
        for action in json_step4:
            actions.append(cls.json_to_action(action))
        return actions

    @classmethod
    def json_to_action(cls, json_action):
        """
        [Natural, [GP, ...], [GB, ...], [BT, ...], [RT, ...]]
        """
        assert(cls.validate_action_json(json_action))
        species_index = json_action[0]
        pop_grows = []
        for i in range(len(json_action[1])):
            gp = json_action[1][i]
            pop_grows.append(PopGrow(gp[1], gp[2]))
        body_grows = []
        for i in range(len(json_action[2])):
            gb = json_action[2][i]
            body_grows.append(BodyGrow(gb[1], gb[2]))
        new_boards = []
        for i in range(len(json_action[3])):
            bt = json_action[3][i]
            traits = bt[1:]
            new_boards.append(BoardAddition(bt[0], traits))
        trait_replacements = []
        for i in range(len(json_action[4])):
            rt = json_action[4][i]
            trait_replacements.append(ReplaceTrait(rt[0], rt[1], rt[2]))

        return Action(species_index, pop_grows, body_grows, new_boards, trait_replacements)

    @classmethod
    def validate_action_json(cls, json_action):
        # TODO
        return True

    @classmethod
    def action_to_json(cls, action):
        gps = map(lambda gp: ["population", gp.species_index, gp.payment_index],
                 action.pop_grows)
        gbs = map(lambda gb: ["body", gb.species_index, gb.payment_index],
                 action.body_grows)
        bts = map(lambda bt: cls.bt_to_json(bt), action.species_additions)
        rts = map(lambda rt: [rt.species_index,
                              rt.removed_trait_index,
                              rt.new_trait_index],
                 action.trait_replacements)
        return [action.food_card, gps, gbs, bts, rts]

    @classmethod
    def bt_to_json(cls, bt):
        bt_json = [bt.payment_index]
        bt_json.extend(bt.traits)
        return bt_json


    @classmethod
    def json_to_feeding(cls, json_feeding):
        assert(self.validate_json_feeding(json_feeding))
        # Python sucks and we should feel bad
        if json_feeding == False and type(json_feeding) is type(False):
            return AbstainFeeding()
        elif isinstance(json_feeding, (int, long)):
            return HerbivoreFeeding(json_feeding)
        elif len(json_feeding) == 2:
            return FatTissueFeeding(json_feeding[0], json_feeding[1])
        else:
            return CarnivoreFeeding(json_feeding[0], json_feeding[1], json_feeding[2])

    @classmethod
    def validate_json_feeding(cls, json_feeding):
        # TODO:
        return True

    @classmethod
    def json_to_trait_card(cls, json_trait_card):
        assert(cls.validate_trait_card_json(json_trait_card))
        return TraitCard(json_trait_card[1], json_trait_card[0])

    @classmethod
    def trait_card_to_json(cls, trait_card):
        return [trait_card.food_points, trait_card.trait]

    @classmethod
    def validate_trait_card_json(cls, json_trait_card):
        return any([(json_trait_card[1] == "carnivore" and
                     json_trait_card[0] <= 8 and
                     json_trait_card[0] >= -8),
                    (json_trait_card[1] != "carnivore" and
                     json_trait_card[0] <= 3 and
                     json_trait_card[0] >= -3)])
