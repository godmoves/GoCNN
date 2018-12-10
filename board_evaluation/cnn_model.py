#!/usr/bin/env python2
import os

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
    def __init__(self, board_size, layers, filters, ckpt_path):
        self.board_size = board_size
        self.layers = layers
        self.filters = filters
        self.sess = tf.InteractiveSession()

        # training op
        self.x, self.y_real = place_holders(board_size=board_size)
        self.y_conv = self.model(self.x, board_size=board_size, filters=filters)
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
        self.saver = tf.train.Saver(tf.global_variables())
        self.ckpt_path = ckpt_path
        self.restore_ckpt()
        self.best_test_accuracy = 0

    def train(self, step, x_batch, y_batch):
        _, loss_value, y_value = self.sess.run(
            [self.train_op, self.loss, self.y_conv], feed_dict={
                self.x: x_batch, self.y_real: y_batch})

        if step % 10 == 0:
            acc = self.accuracy.eval(feed_dict={self.x: x_batch, self.y_real: y_batch})
            print("step=%d, loss=%f, acc=%f" % (step, loss_value, acc))

    def model(self, x, board_size=19, filters=64):
        # the layer number here is not configurable, I will fix this later
        x_board = tf.reshape(x, [-1, board_size, board_size, 8])
        W_conv1 = weight_variable([5, 5, 8, filters])
        b_conv1 = bias_variable([filters])
        h_conv1 = tf.nn.relu(conv2d(x_board, W_conv1) + b_conv1)

        W_conv2 = weight_variable([5, 5, filters, filters])
        b_conv2 = bias_variable([filters])
        h_conv2 = tf.nn.relu(conv2d(h_conv1, W_conv2) + b_conv2)

        W_conv3 = weight_variable([5, 5, filters, filters])
        b_conv3 = bias_variable([filters])
        h_conv3 = tf.nn.relu(conv2d(h_conv2, W_conv3) + b_conv3)

        W_conv4 = weight_variable([5, 5, filters, filters])
        b_conv4 = bias_variable([filters])
        h_conv4 = tf.nn.relu(conv2d(h_conv3, W_conv4) + b_conv4)

        W_conv5 = weight_variable([5, 5, filters, filters])
        b_conv5 = bias_variable([filters])
        h_conv5 = tf.nn.relu(conv2d(h_conv4, W_conv5) + b_conv5)

        # Final outputs from layer 5
        W_convm5 = weight_variable([5, 5, filters, 1])
        b_convm5 = bias_variable([1])
        h_convm5 = conv2d(h_conv5, W_convm5) + b_convm5

        pred_ownership = tf.sigmoid(tf.reshape(h_convm5, [-1, board_size**2]))
        return pred_ownership

    def loss_function(self, y_pred, y_true):
        loss = tf.reduce_mean(tf.pow(y_pred - y_true, 2))
        return loss

    def train_step(self, loss):
        return tf.train.AdamOptimizer(1e-4).minimize(loss)

    def restore_ckpt(self):
        ckpt_dir, _ = os.path.split(self.ckpt_path)
        ckpt = tf.train.latest_checkpoint(ckpt_dir)
        if ckpt is not None:
            print("restore from previous checkpoint")
            self.saver.restore(self.sess, ckpt)

    def save_ckpt(self, test_accuracy, only_keep_best=True):
        # by default, we only keep the net with best test accuracy
        print("Test accuracy: %f" % test_accuracy)
        if only_keep_best:
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
