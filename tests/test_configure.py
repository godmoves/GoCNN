#!/usr/bin/env python2

import os

input_dir = "./tests/data/raw/"
output_dir = "./tests/data/input/"
completed_dir = "./tests/data/gnugo/"
board_size = 9
ownership = True


def rm_test_outputs(path, suffix):
    for subdir, dirs, files in os.walk(path):
        for file in files:
            filepath = os.path.join(subdir, file)
            if filepath.endswith(suffix):
                os.remove(filepath)
