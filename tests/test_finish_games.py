import os
import unittest

from munge.finish_games import finish_sgf_and_get_ownership
from munge.finish_games import finish_sgf
from munge.finish_games import run_gungo
from tests.test_configure import *


class TestFinishGames(unittest.TestCase):
    def test_finish_games(self):
        sgf_name = "test_b+1.sgf"
        sgf_filepath = input_dir + sgf_name

        black_ownership, white_ownership = finish_sgf_and_get_ownership(
            sgf_filepath, sgf_name, completed_dir, board_size,
            difference_threshold=100, year_lowerbound=0)

        for i in reversed(range(board_size)):
            row_str = ""
            for j in range(board_size):
                row_str += str(int(black_ownership[i][j]))
            print(row_str)
        print("")


class TestFinishSgf(unittest.TestCase):
    def test_finish_sgf(self):
        sgf_name = "test_b+1.sgf"
        sgf_filepath = input_dir + sgf_name
        dest_file = completed_dir + sgf_name[:-4] + ".sgfc"

        finish_sgf(sgf_filepath, dest_file, board_size, difference_threshold=100,
                   year_lowerbound=0, gnugo_timeout=10)


class TestGnugo(unittest.TestCase):
    def test_gnugo(self):
        gnugo_path = os.getcwd() + "/gnugo"
        test_files = ["test_b+r.sgf", "test_draw.sgf", "test_b+1.sgf"]

        for f in test_files:
            sgf_name = f
            sgf_filepath = input_dir + sgf_name
            dest_file = completed_dir + sgf_name[:-4] + ".sgfc"
            run_gungo(gnugo_path, sgf_filepath, dest_file)
            os.remove(dest_file)


if __name__ == '__main__':
    unittest.main()