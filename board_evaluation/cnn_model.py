#!/usr/bin/env python2
from __future__ import print_function
import os
import sys

import tensorflow as tf


def weight_variable(shape):
    initial = tf.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial)


def bias_variable(shape):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)


def conv2d(x, W):
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')


def place_holders(board_size=19):
    x = tf.placeholder("float", shape=[None, board_size, board_size, 8])
    ownership = tf.placeholder("float", shape=[None, board_size**2])
    return x, ownership


class CNNModel():
    def __init__(self, board_size, layers, filters, ckpt_dir):
        self.board_size = board_size
        self.layers = layers
        self.filters = filters
        self.sess = tf.InteractiveSession()

        # training op
        self.x, self.y_real = place_holders(self.board_size)
        self.y_conv = self.model(self.x)
        self.loss = self.loss_function(self.y_real, self.y_conv)
        self.train_op = self.train_step(self.loss)

        # evaluation stuff
        prediction = tf.round(self.y_conv)
        self.correct_prediction = tf.equal(self.y_real, prediction)
        self.correct_count = tf.reduce_sum(tf.cast(self.correct_prediction, "float"))
        self.accuracy = tf.reduce_mean(tf.cast(self.correct_prediction, "float"))

        # initialize
        self.sess.run(tf.global_variables_initializer())

        # save & restore configuration
        self.best_test_accuracy = 0
        self.saver = tf.train.Saver(tf.global_variables())
        if ckpt_dir is not None:
            self.ckpt_dir = ckpt_dir
            self.ckpt_name = 'cnn_{}layer_{}filter'.format(self.layers, self.filters)
            self.ckpt_path = os.path.join(self.ckpt_dir, self.ckpt_name)
            self.restore_ckpt()

    def train(self, step, x_batch, y_batch):
        _, loss_value, y_value = self.sess.run(
            [self.train_op, self.loss, self.y_conv], feed_dict={
                self.x: x_batch, self.y_real: y_batch})

        if step % 10 == 0:
            acc = self.accuracy.eval(feed_dict={self.x: x_batch, self.y_real: y_batch})
            print("step=%d, loss=%f, acc=%f" % (step, loss_value, acc))

    def conv_layer(self, x, filters, name='conv'):
        with tf.name_scope(name):
            W = weight_variable([5, 5, filters, filters])
            b = bias_variable([filters])
            h = tf.nn.relu(conv2d(x, W) + b)
        return h

    def model(self, x):
        x_board = tf.reshape(x, [-1, self.board_size, self.board_size, 8])
        W_conv_first = weight_variable([5, 5, 8, self.filters])
        b_conv_first = bias_variable([self.filters])
        x = tf.nn.relu(conv2d(x_board, W_conv_first) + b_conv_first)

        for i in range(self.layers - 1):
            x = self.conv_layer(x, self.filters, name='conv_' + str(i))

        # outputs from final layer
        W_conv_final = weight_variable([5, 5, self.filters, 1])
        b_conv_final = bias_variable([1])
        h_conv_final = conv2d(x, W_conv_final) + b_conv_final

        pred_ownership = tf.sigmoid(tf.reshape(h_conv_final, [-1, self.board_size**2]))
        return pred_ownership

    def loss_function(self, y_pred, y_true):
        loss = tf.reduce_mean(tf.pow(y_pred - y_true, 2))
        return loss

    def train_step(self, loss):
        return tf.train.AdamOptimizer(1e-4).minimize(loss)

    def restore_ckpt(self):
        ckpt = tf.train.latest_checkpoint(self.ckpt_dir)
        if ckpt is not None:
            print("restore from previous checkpoint", file=sys.stderr)
            self.saver.restore(self.sess, ckpt)

    def save_ckpt(self, test_accuracy, keep_best_only=True):
        # by default, we only keep the net with best test accuracy
        print("Test accuracy: %f" % test_accuracy)
        if keep_best_only:
            if test_accuracy > self.best_test_accuracy:
                print("New best test accuracy, saving checkpoint...")
                self.saver.save(self.sess, self.ckpt_path)
                self.best_test_accuracy = test_accuracy
            else:
                print('Test accuracy %s less than %s, no progress...' % (
                    test_accuracy, self.best_test_accuracy))
        else:
            print('Saving checkpoint...')
            self.saver.save(self.sess, self.ckpt_path)
