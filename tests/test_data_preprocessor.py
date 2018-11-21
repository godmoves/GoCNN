import unittest

from munge.data_preprocessor import munge_all_sgfs
from munge.data_preprocessor import walkthroughSgf
from tests.test_configure import *


class TestMungeAll(unittest.TestCase):
    def test_munge_all(self):
        munge_all_sgfs(input_dir, output_dir, completed_dir, board_size, ownership)


class TestSgfProcess(unittest.TestCase):
    def test_sgf_process(self):
        sgf_name = "test_b+1.sgf"
        sgf_filepath = input_dir + sgf_name
        sgf_file = open(sgf_filepath, 'r')
        sgf_contents = sgf_file.read()
        sgf_file.close()

        walkthroughSgf(sgf_contents, sgf_filepath, sgf_name, output_dir,
                       completed_dir, board_size, ownership)


if __name__ == '__main__':
    unittest.main()
