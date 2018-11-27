#!/usr/bin/env python2
import unittest
import numpy as np

from thirdparty.GoBoard import GoBoard
from thirdparty.GoString import GoString


class TestGOBoard(unittest.TestCase):
    def test_addAdjacentLiberty(self):
        gs = GoString(boardSize=3, color='b')
        gb = GoBoard(boardSize=3)
        gb.addAdjacentLiberty((1, 2), gs)
        target = "Bag2d\n...\n..*\n...\n"
        self.assertEqual(gs.libStr(), target)

    def test_createPointString(self):
        gb = GoBoard(boardSize=3)
        ps = gb.createPointString('b', (1, 1))
        target_libstr = "Bag2d\n.*.\n*.*\n.*.\n"
        target_piestr = "Bag2d\n...\n.*.\n...\n"

        self.assertEqual(ps.libStr(), target_libstr)
        self.assertEqual(ps.pieStr(), target_piestr)

    def test_otherColor(self):
        gb = GoBoard(boardSize=3)
        b = gb.otherColor('w')
        w = gb.otherColor('b')

        self.assertEqual(b, 'b')
        self.assertEqual(w, 'w')

    def test_playOnExistStone(self):
        gb = GoBoard(boardSize=5)
        gb.applyMove('b', (0, 2))
        try:
            gb.applyMove('b', (0, 2))
        except ValueError:
            print('play on exist stone')

    def test_isSimpleKo(self):
        gb = GoBoard(boardSize=5)
        gb.applyMove('b', (0, 2))
        gb.applyMove('w', (2, 1))
        gb.applyMove('b', (1, 1))
        gb.applyMove('w', (3, 2))
        gb.applyMove('b', (1, 3))
        gb.applyMove('w', (2, 3))
        gb.applyMove('b', (2, 2))
        gb.applyMove('w', (1, 2))
        self.assertEqual(gb.ko_lastMove, (1, 2))
        self.assertTrue(gb.isSimpleKo('b', (2, 2)))

    def test_applyMove(self):
        gb = GoBoard(boardSize=3)
        gb.applyMove('b', (0, 0))
        gb.applyMove('b', (0, 1))
        gb.applyMove('b', (1, 0))
        gb.applyMove('b', (1, 1))
        gb.applyMove('w', (2, 0))
        gb.applyMove('w', (2, 1))
        gb.applyMove('w', (2, 2))
        gb.applyMove('w', (1, 2))
        gb.applyMove('w', (0, 2))
        target = 'GoBoard\nOOO\n..O\n..O\n'
        self.assertEqual(str(gb), target)

        gb.applyMove('w', (0, 0))
        target = 'GoBoard\nOOO\n..O\nO.O\n'
        self.assertEqual(str(gb), target)

    def test_get_final_ownership(self):
        gb = GoBoard(boardSize=5)
        gb.applyMove('b', (0, 0))
        gb.applyMove('b', (1, 1))
        gb.applyMove('b', (2, 2))
        gb.applyMove('b', (3, 3))
        gb.applyMove('b', (4, 4))
        gb.applyMove('w', (0, 1))
        gb.applyMove('w', (1, 2))
        gb.applyMove('w', (2, 3))
        gb.applyMove('w', (3, 4))
        black_own = gb.get_final_ownership('b')
        white_own = gb.get_final_ownership('w')

        target_black_own = np.array([[1, 0, 0, 0, 0],
                                     [1, 1, 0, 0, 0],
                                     [1, 1, 1, 0, 0],
                                     [1, 1, 1, 1, 0],
                                     [1, 1, 1, 1, 1]])
        target_white_own = np.array([[0, 1, 1, 1, 1],
                                     [0, 0, 1, 1, 1],
                                     [0, 0, 0, 1, 1],
                                     [0, 0, 0, 0, 1],
                                     [0, 0, 0, 0, 0]])

        assert (black_own == target_black_own).all()
        assert (white_own == target_white_own).all()
