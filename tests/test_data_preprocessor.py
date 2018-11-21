import os
import unittest

from munge.data_preprocessor import munge_all_sgfs
from munge.data_preprocessor import walkthroughSgf
from tests.test_configure import *


def rm_test_files(path, suffix):
    for subdir, dirs, files in os.walk(path):
        for file in files:
            filepath = os.path.join(subdir, file)
            if filepath.endswith(suffix):
                os.remove(filepath)


class TestMungeAll(unittest.TestCase):
    def test_munge_all(self):
        munge_all_sgfs(input_dir, output_dir, completed_dir, board_size, ownership)
        rm_test_files(completed_dir, ".sgfc")
        rm_test_files(output_dir, ".dat")


class TestSgfProcess(unittest.TestCase):
    def test_sgf_process(self):
        test_files = ["test_b+1.sgf", "test_draw.sgf", "test_b+r.sgf"]

        for f in test_files:
            sgf_name = f
            sgf_filepath = input_dir + sgf_name
            sgf_file = open(sgf_filepath, 'r')
            sgf_contents = sgf_file.read()
            sgf_file.close()

            out_filepath = os.path.join(output_dir, sgf_name[:-4]) + ".dat"

            walkthroughSgf(sgf_contents, sgf_filepath, sgf_name, out_filepath,
                           completed_dir, board_size, ownership)

        rm_test_files(completed_dir, ".sgfc")
        rm_test_files(output_dir, ".dat")


if __name__ == '__main__':
    unittest.main()
