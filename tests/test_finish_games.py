#!/usr/bin/env python2
import os
import unittest

from munge.finish_games import finish_sgf_and_get_ownership
from munge.finish_games import finish_sgf
from munge.finish_games import run_gungo
from munge.finish_games import parse_sgf_result
from tests.test_configure import *


class TestFinishGames(unittest.TestCase):
    def test_finish_games(self):
        sgf_name = "test_draw.sgf"
        sgf_filepath = os.path.join(input_dir, sgf_name)

        black_ownership, white_ownership = finish_sgf_and_get_ownership(
            sgf_filepath, sgf_name, completed_dir, board_size,
            difference_threshold=100, year_lowerbound=0)

        self.assertIsNotNone(black_ownership)
        self.assertIsNotNone(white_ownership)

        rm_test_outputs(completed_dir, ".sgfc")


class TestFinishSgf(unittest.TestCase):
    def test_finish_sgf(self):
        sgf_name = "test_draw.sgf"
        sgf_filepath = os.path.join(input_dir, sgf_name)
        dest_file = os.path.join(completed_dir + sgf_name[:-4]) + ".sgfc"

        res = finish_sgf(sgf_filepath, dest_file, board_size, difference_threshold=100,
                         year_lowerbound=0, gnugo_timeout=10)
        self.assertTrue(res)


class TestParseResult(unittest.TestCase):
    def test_parse_result(self):
        sgf_name = "test_b+r.sgf"
        sgf_filepath = os.path.join(input_dir, sgf_name)

        sgf_file = open(sgf_filepath, 'r')
        sgf_contents = sgf_file.read()
        sgf_file.close()

        valid, _ = parse_sgf_result(sgf_filepath, sgf_contents, board_size)
        self.assertTrue(valid)


class TestGnugo(unittest.TestCase):
    def test_gnugo(self):
        gnugo_path = os.path.join(os.getcwd(), "gnugo")
        test_files = ["test_b+r.sgf", "test_draw.sgf", "test_b+1.sgf"]

        for sgf_name in test_files:
            sgf_filepath = os.path.join(input_dir, sgf_name)
            dest_file = os.path.join(completed_dir, sgf_name[:-4]) + ".sgfc"
            output = run_gungo(gnugo_path, sgf_filepath, dest_file)

            self.assertIsNotNone(output)
            os.remove(dest_file)


if __name__ == '__main__':
    unittest.main()
