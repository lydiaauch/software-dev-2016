from globals import *


class Species(object):
    """
    A data representation of a Species in the Evolution game

    Attributes:
        population: The population of the species
        food: the number of food tokens the species has
        body: the body size of the species
        traits: a List of TraitCards the species has
        fat_storage: the number of fat-food tokens the species has
        id: a unique ID for the species
    """
    uuid = 0

    @classmethod
    def gen_id(cls):
        """
        Generates a unique id using an incremental counter.
        """
        cls.uuid += 1
        return cls.uuid

    def __init__(self, population=None, food=None, body=None, traits=None, fat_storage=None):
        if population is None:
            population = 1
        if food is None:
            food = 0
        if body is None:
            body = 0
        if traits is None:
            traits = []
        if fat_storage is None:
            fat_storage = 0

        self.population = population
        self.food = food
        self.body = body
        self.traits = traits
        self.fat_storage = fat_storage
        self.id = Species.gen_id()

    def __str__(self):
        return "Species(pop=%d, food=%d, body=%d, traits=%s id=%d" \
               % (self.population, self.food, self.body, self.traits, self.id)

    def __eq__(self, other):
        return all([isinstance(other, Species),
                    self.population == other.population,
                    self.food == other.food,
                    self.body == other.body,
                    self.traits == other.traits,
                    self.fat_storage == other.fat_storage,
                    self.id == other.id])

    def is_attackable(self, attacker, left_neighbor=False, right_neighbor=False):
        """
        Determines if this species is attackable by the attacker species,
        given its two neighbors
        :param attacker: the Species attacking this species
        :param left_neighbor: the Species to the left of this species
                              (False if no left neighbor)
        :param right_neighbor: the Species to the right of this species
                               (False if no left neighbor)
        :return: True if attackable, else false
        """
        defender_traits = self.traits
        attacker_traits = attacker.traits
        left_traits = left_neighbor.traits if left_neighbor else []
        right_traits = right_neighbor.traits if right_neighbor else []
        attacker_body = attacker.body + (attacker.population if "pack-hunting" in attacker_traits
                                         else 0)

        return not any(["carnivore" not in attacker_traits,
                        "burrowing" in defender_traits and self.food == self.population,
                        "climbing" in defender_traits and "climbing" not in attacker_traits,
                        "hard-shell" in defender_traits and
                        attacker_body - self.body < HARD_SHELL_DIFF,
                        "herding" in defender_traits and attacker.population <= self.population,
                        "symbiosis" in defender_traits and
                        right_neighbor and right_neighbor.body > self.body,
                        (("warning-call" in right_traits) or ("warning-call" in left_traits)) and
                        "ambush" not in attacker_traits])

    def can_eat(self):
        """
        Deternmines if a species can eat more food tokens.
        :return:  True if the species can eat, else false.
        """
        if "fat-tissue" in self.traits:
            return self.fat_storage < self.body or self.food < self.population
        else:
            return self.food < self.population

    def digest_fat(self):
        """
        Metabolize fat food. ie move fat food onto food amount.
        """
        can_move = min(self.population - self.food, self.fat_storage)
        self.fat_storage -= can_move
        self.food += can_move

    def breed(self):
        """
        Increases the population of this species by one if possible.
        """
        if self.population < MAX_POPULATION:
            self.population += 1

    def grow_body(self):
        """
        Increases the body size of this species by one if possible.
        """
        if self.body < MAX_BODY_SIZE:
            self.body += 1

    def kill(self):
        """
        Decreases the population of this species by one, reducing food if necessary.
        """
        self.population -= 1
        self.food = min(self.population, self.food)

    def is_extinct(self):
        """
        Checks if this species is extinct, ie. population = 0.
        """
        return self.population == 0

    def replace_trait(self, trait_index, trait):
        """
        Removes the trait at the given index, replacing it with the given trait.
        :param trait_index: Index of the trait to be replaced. Must be < len(self.traits)
        :param trait: String of the new trait's name.
        """
        self.traits[trait_index] = trait