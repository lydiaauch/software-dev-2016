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
        else:
            raise Exception("Given invalid trait: {0}".format(trait))

    def __str__(self):
        return "TraitCard(trait=%s, food=%d)" % (self.trait, self.food_points)

    def __eq__(self, other):
        return all([isinstance(other, TraitCard),
                    self.trait == other.trait,
                    self.food_points == other.food_points])
