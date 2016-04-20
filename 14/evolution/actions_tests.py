import unittest
from actions import *


class TestActions(unittest.TestCase):
    def test_has_unique_indices(self):
        good_action = Action(0,
                             [PopGrow(0, 1)],
                             [BodyGrow(0, 2)],
                             [BoardAddition(3, [4, 5, 6])],
                             [ReplaceTrait(0, 0, 7)])
        self.assertTrue(good_action.has_unique_indices())
        bad_action = Action(0,
                            [PopGrow(0, 1)],
                            [BodyGrow(0, 1)],
                            [BoardAddition(3, [4, 5, 6])],
                            [ReplaceTrait(0, 0, 7)])
        self.assertFalse(bad_action.has_unique_indices())
        bad_action = Action(0,
                            [PopGrow(0, 1)],
                            [BodyGrow(0, 2)],
                            [BoardAddition(1, [4, 5, 6])],
                            [ReplaceTrait(0, 0, 7)])
        self.assertFalse(bad_action.has_unique_indices())
        bad_action = Action(0,
                            [PopGrow(0, 1)],
                            [BodyGrow(0, 2)],
                            [BoardAddition(3, [4, 0, 6])],
                            [ReplaceTrait(0, 0, 7)])
        self.assertFalse(bad_action.has_unique_indices())
        bad_action = Action(0,
                            [PopGrow(0, 1)],
                            [BodyGrow(0, 1)],
                            [BoardAddition(3, [4, 5, 6])],
                            [ReplaceTrait(0, 0, 0)])
        self.assertFalse(bad_action.has_unique_indices())


if __name__ == '__main__':
    unittest.main()
