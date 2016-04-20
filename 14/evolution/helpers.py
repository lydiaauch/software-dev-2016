from functools import wraps
import errno
import os
import signal


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


class TimeoutError(Exception):
    pass


def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator


def is_unique_list(li):
    """
    Checks that no two elements in the list are the same.
    :param li: The List of anything to check.
    :return: True if the list has only unique elements, False if there are any duplicates.
    """
    remaining = [elem for elem in li]
    while remaining:
        if remaining[0] in remaining[1:]:
            return False
        else:
            remaining = remaining[1:]
    return True


def print_results(dealer, messages):
    """
    Prints player ID's and scores in descending order. Each player in the dealer
    has an associated message in the messages list to print along with their score.
    :param dealer: A Dealer object representing the game to print.
    :param messages: A list of Strings representing each player's tag line.
    """
    results = ""
    players = zip(dealer.players, messages)
    players.sort(cmp=lambda p1, p2: p2[0].food_bag - p1[0].food_bag)
    for index, player in enumerate(players):
        results += "%d player id: %d tag: %s score: %d\n" % \
            (index + 1, player[0].name, player[1], player[0].food_bag)
    return results
