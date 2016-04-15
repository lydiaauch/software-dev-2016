def carnivore_targets(carnivore, list_of_player):
    """
    Creates a list of all possible targets for given carnivore from the list of
    players.
    :param: carnivore The attacking carnivore.
    :param: list_of_player All players to be considered for possible targets.
    """
    targets = []
    for player in list_of_player:
        for i in range(0, len(player.species)):
            defender = player.species[i]
            left_neighbor = (False if i == 0 else player.species[i - 1])
            right_neighbor = (False if i == len(player.species) - 1
                              else player.species[i + 1])
            if defender.is_attackable(carnivore, left_neighbor, right_neighbor) \
               and defender != carnivore:
                targets.append(defender)
    return targets
