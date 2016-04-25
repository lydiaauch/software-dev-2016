from functools import wraps
import errno
import os
import signal
from globals import TIMEOUT

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


def timeout(seconds=TIMEOUT, error_message=os.strerror(errno.ETIME)):
    """
    Defines a function decorator to define functions with a timeout.
    Starts a signal with its time set to the timeout amount which raises a
    TimeoutError if the time limit is reached, otherwise the functions value
    is returned and no error is raised.
    Usage:
    @timeout(20)
    def func(self):
        ...
    Defines the function func with a timeout of 20 seconds before the error is
    raised.
    :param seconds: The number of seconds to run the function for.
    :param error_message: The message to run in the event of a timeout.
    """
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


class TimeoutError(Exception):
    pass


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


def print_results(scores, messages=None):
    """
    Prints player ID's and scores in descending order. Each player in the dealer
    has an associated message in the messages list to print along with their score.
    :param scores: A list of lists of player id and player score.
    :param messages: A list of Strings representing each player's tag line.
    """
    if not messages:
        messages = map(lambda x: "", scores)

    scores.sort(cmp=lambda l1, l2: l2[1] - l1[1])
    results = ""
    index = 1
    for elem in scores:
        id = elem[0]
        score = elem[1]
        results += "%d player id: %d tag: %s score: %d\n" % \
            (index, id, messages[id - 1], score)
        index += 1
    return results
