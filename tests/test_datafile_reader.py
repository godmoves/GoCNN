#!/usr/bin/env python2

import unittest

from board_evaluation.go_datafile_reader import RandomAccessFileReader
from tests.test_configure import *


class TestRandomAccessFileReader(unittest.TestCase):
    def test_random_access_file_reader(self):
        files = ["./tests/data/test.dat"]
        RandomAccessFileReader(files, board_size)


class TestSeekRandomPlace(unittest.TestCase):
    def test_seek_random_place(self):
        file_name = "./tests/data/test.dat"
        with open(file_name) as f:
            RandomAccessFileReader._seek_random_place_in_file(f, board_size)


if __name__ == '__main__':
    unittest.main()
