#!/usr/bin/env python2
import unittest
from thirdparty.bag2d import Bag2d


class TestBag2d(unittest.TestCase):
    def test_init(self):
        bag2d = Bag2d(boardSize=3)
        target = "Bag2d\n...\n...\n...\n"
        self.assertEqual(str(bag2d), target)

    def test_insert(self):
        bag2d = Bag2d(boardSize=3)
        combo = (1, 2)
        bag2d.insert(combo)
        target = "Bag2d\n...\n..*\n...\n"
        self.assertEqual(str(bag2d), target)

    def test_erase(self):
        bag2d = Bag2d(boardSize=3)
        combo1 = (1, 2)
        combo2 = (1, 1)
        bag2d.insert(combo1)
        bag2d.erase(combo2)
        target = "Bag2d\n...\n..*\n...\n"
        self.assertEqual(str(bag2d), target)

        bag2d.erase(combo1)
        target = "Bag2d\n...\n...\n...\n"
        self.assertEqual(str(bag2d), target)

    def test_exist(self):
        bag2d = Bag2d(boardSize=3)
        combo1 = (1, 2)
        bag2d.insert(combo1)
        result = bag2d.exists(combo1)
        self.assertTrue(result)

        combo2 = (2, 2)
        result = bag2d.exists(combo2)
        self.assertFalse(result)

    def test_size(self):
        bag2d = Bag2d(boardSize=3)
        self.assertEqual(bag2d.size(), 0)

        combo1 = (1, 2)
        bag2d.insert(combo1)
        self.assertEqual(bag2d.size(), 1)

    def test_get_item(self):
        bag2d = Bag2d(boardSize=3)
        combo1 = (1, 2)
        bag2d.insert(combo1)
        combo2 = (0, 0)
        bag2d.insert(combo2)
        result1 = bag2d[0]
        result2 = bag2d[1]

        self.assertEqual(result1, combo1)
        self.assertEqual(result2, combo2)


if __name__ == '__main__':
    unittest.main()
