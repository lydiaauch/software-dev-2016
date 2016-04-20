class Choice(object):
    """
    Describes the data a Player needs to make their Action for this turn.
    """

    def __init__(self, before, after):
        """
        :param player: The PlayerState of the current Player.
        :param before: The Listof Listof Species where each list represents the
        species of a Player before the current player.
        :param after: The Listof Listof Species where each list represents the
        species of a Player after the current player.
        """
        self.before = before
        self.after = after
