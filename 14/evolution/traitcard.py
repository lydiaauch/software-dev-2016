class TraitCard(object):
    """
    A Trait Card of the Evolution game
    """

    traits = ["carnivore",
              "ambush",
              "burrowing",
              "climbing",
              "cooperation",
              "fat-tissue",
              "fertile",
              "foraging",
              "hard-shell",
              "herding",
              "horns",
              "long-neck",
              "pack-hunting",
              "scavenger",
              "symbiosis",
              "warning-call"]

    def __init__(self, trait, food_points=0):
        if any(trait == t for t in self.traits):
            self.trait = trait
            self.food_points = food_points
            self.used = False
        else:
            raise Exception("Given invalid trait: {0}".format(trait))

    def __str__(self):
        return "[%d, %s]" % (self.food_points, self.trait)

    def __eq__(self, other):
        return all([isinstance(other, TraitCard),
                    self.trait == other.trait,
                    self.food_points == other.food_points])

    @classmethod
    def gen_cards(cls, num_cards, trait_name):
        """
        Generates num_cards trait cards with the given trait_name and food points.
        If the card generated is a carnivore, the range of food_points is (-8,8),
        else the range of food_points is (-3, 3).
        """
        cards = []
        cards.append(TraitCard(trait_name, 0))
        for num in range(num_cards / 2):
            cards.append(TraitCard(trait_name, num + 1))
            cards.append(TraitCard(trait_name, -1 * (num + 1)))
        return cards

    @classmethod
    def compare(cls, c1, c2):
        """
        Compares two trait cards. Returns -1 if c1 is less than c2, or 1 if
        c1 is larger than c2.
        """
        if c1.trait == c2.trait:
            if c1.food_points < c2.food_points:
                return -1
            else:
                return 1
        else:
            if c1.trait < c2.trait:
                return -1
            else:
                return 1
