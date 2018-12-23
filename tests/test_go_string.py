#!/usr/bin/env python2
import unittest
from thirdparty.go_string import GoString


class TestGoString(unittest.TestCase):
    def test_insert_piece(self):
        gs = GoString(boardSize=3, color='black')
        combo = (1, 2)
        gs.insertPiece(combo)


if __name__ == '__main__':
    unittest.main()
