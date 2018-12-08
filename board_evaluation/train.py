#!/usr/bin/env python2
import os

import numpy as np

from board_evaluation.cnn_model import CNNModel
from board_evaluation.model_utils import test_accuracy
from board_evaluation.datafile_reader import GoDatafileReader
from board_evaluation.datafile_reader import RandomAccessFileReader


def rolling_mean(number_list, window=20):
    means = np.zeros(len(number_list))
    for i in range(len(means)):
        sub_window = number_list[i - window + 1: i + 1]
        means[i] = np.mean(sub_window)
    return means


def read_data_from_dir(data_dir):
    data_files = []
    for subdir, dirs, files in os.walk(data_dir):
        for file in files:
            filepath = subdir + os.sep + file
            if filepath.endswith(".dat"):
                data_files.append(filepath)
    return data_files


def nn_trainer(train_dir, test_dir, ckpt_path, board_size, total_steps=100000):
    train_files = read_data_from_dir(train_dir)
    test_files = read_data_from_dir(test_dir)

    print("num train: %d, num test: %d" % (len(train_files), len(test_files)))

    # note you may have to change the os limit for number of open files to use the
    # RandomAccessFileReader, you can do this with the command "sudo ulimit -n 20000"
    # if sudo can't find the ulimit command try the following below:
    # sudo sh -c "ulimit -n 20000 && exec su $LOGNAME"
    reader = RandomAccessFileReader(train_files, board_size)
    test_reader = GoDatafileReader(test_files, board_size)

    test_reader.num_epochs = 0
    test_features = []
    test_targets = []
    while test_reader.num_epochs == 0:
        final_state, _, feature_cube = test_reader.read_sample()
        test_features.append(feature_cube)
        test_targets.append(final_state)

    # TODO: the layer number is actually fixed now. We want to change it laster
    # to test the performance of different architectures.
    model = CNNModel(board_size=9, layers=5, filters=64, ckpt_path=ckpt_path)

    for step in range(total_steps):
        x_batch, y_batch = reader.get_batch(64)

        model.train(step, x_batch, y_batch)

        if step % 1000 == 0:
            test_acc = test_accuracy(test_features, test_targets, model)
            model.save_ckpt(test_acc, only_keep_best=True)
