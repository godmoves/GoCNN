#!/usr/bin/env python2
import os
import sys

import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt

from board_evaluation import go_datafile_reader
from board_evaluation import model
from board_evaluation import model_eval


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

    x, ownership = model.place_holders(board_size=9)
    y_conv = model.model(x, board_size=9)
    loss = model.loss_function(ownership, y_conv)
    train_op = model.train_step(loss)

    prediction = tf.round(y_conv)
    correct_prediction = tf.equal(ownership, prediction)
    correct_count = tf.reduce_sum(tf.cast(correct_prediction, "float"))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))

    sess = tf.InteractiveSession()
    sess.run(tf.global_variables_initializer())
    saver = tf.train.Saver(tf.global_variables())

    ckpt_dir, _ = os.path.split(ckpt_path)
    ckpt = tf.train.latest_checkpoint(ckpt_dir)
    if ckpt is not None:
        print("restore from previous checkpoint")
        saver.restore(sess, ckpt)

    training_accuracies = []
    test_accuracies = []
    for k in range(total_steps):
        x_batch, y_batch = reader.get_batch(50)
        _, loss_value, y_value = sess.run([train_op, loss, y_conv], feed_dict={
                                          x: x_batch, ownership: y_batch})
        if k % 10 == 0:
            acc = accuracy.eval(feed_dict={x: x_batch, ownership: y_batch})
            training_accuracies.append(acc)
            print("step=%d, loss=%f. acc=%f" % (k, loss_value, acc))

        if k % 1000 == 0:
            test_accuracy = model_eval.test_accuracy(
                test_features, test_targets, x, ownership, correct_count)
            test_accuracies.append(test_accuracy)
            print("Test accuracy: %f" % test_accuracy)
        if k % 1000 == 0:
            print("Saving Checkpoint...")
            saver.save(sess, ckpt_path)
