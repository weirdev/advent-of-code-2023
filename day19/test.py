import unittest

from main import Condition

class TestCondition(unittest.TestCase):
    def test_check_condition(self) -> None:
        cond = Condition('a', '>', 3)
        self.assertTrue(cond({'a': 4}))
        self.assertFalse(cond({'a': 3}))
        self.assertFalse(cond({'a': 2}))
        with self.assertRaises(KeyError):
            cond({'b': 4})

    def test_apply_to_bounds(self) -> None:
        bounds = {'a': (1, 8)}
        bounds = Condition('a', '>', 3).apply_to_bounds(bounds)
        self.assertEqual(bounds['a'], (4, 8))
        bounds = Condition('a', '>', 2).apply_to_bounds(bounds)
        self.assertEqual(bounds['a'], (4, 8))
        bounds = Condition('a', '<', 8).apply_to_bounds(bounds)
        self.assertEqual(bounds['a'], (4, 7))
        bounds = Condition('a', '<', 4).apply_to_bounds(bounds)
        self.assertIsNone(bounds)


if __name__ == '__main__':
    unittest.main()
