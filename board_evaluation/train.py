import os
import sys

import numpy as np
import tensorflow as tf

from board_evaluation import go_datafile_reader
from board_evaluation import model
from board_evaluation import model_eval


def read_data_from_dir(data_dir):
    data_files = []
    for subdir, dirs, files in os.walk(data_dir):
        for file in files:
            filepath = subdir + os.sep + file
            if filepath.endswith(".dat"):
                data_files.append(filepath)
    return data_files


def nn_trainer(train_dir, test_dir, board_size):
    train_files = read_data_from_dir(train_dir)
    test_files = read_data_from_dir(test_dir)

    print("num train: %d, num test: %d" % (len(train_files), len(test_files)))

    # note you may have to change the os limit for number of open files to use the
    # RandomAccessFileReader, you can do this with the command "sudo ulimit -n 20000"
    # if sudo can't find the ulimit command try the following below:
    # sudo sh -c "ulimit -n 20000 && exec su $LOGNAME"
    reader = go_datafile_reader.RandomAccessFileReader(train_files, board_size)
    test_reader = go_datafile_reader.GoDatafileReader(test_files, board_size)

    test_reader.num_epochs = 0
    test_features = []
    test_targets = []
    test_move_numbers = []
    while(test_reader.num_epochs == 0):
        test_move_numbers.append(test_reader.move_index)
        final_state, _, feature_cube = test_reader.read_sample()
        test_features.append(feature_cube)
        test_targets.append(final_state)

    print(len(reader.open_files))
