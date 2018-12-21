#!/usr/bin/env python2

# BoardEvaluator.py
import os
from board_evaluation.cnn_model import CNNModel
import numpy as np


# this funtion is related to addToDataFile in munge/data_preprocessor
def _board_to_feature_cube(goBoard, color_to_move, board_size, feature_size=8):
    enemy_color = goBoard.otherColor(color_to_move)
    feature_cube = np.zeros((board_size, board_size, feature_size))
    for row in range(goBoard.boardSize):
        for col in range(goBoard.boardSize):
            pos = (row, col)
            if goBoard.board.get(pos) == color_to_move:
                if goBoard.goStrings[pos].liberties.size() == 1:
                    feature_cube[row][col][0] = 1.0
                elif goBoard.goStrings[pos].liberties.size() == 2:
                    feature_cube[row][col][1] = 1.0
                else:
                    feature_cube[row][col][2] = 1.0
            if goBoard.board.get(pos) == enemy_color:
                if goBoard.goStrings[pos].liberties.size() == 1:
                    feature_cube[row][col][3] = 1.0
                elif goBoard.goStrings[pos].liberties.size() == 2:
                    feature_cube[row][col][4] = 1.0
                else:
                    feature_cube[row][col][5] = 1.0
            if goBoard.isSimpleKo(color_to_move, pos):  # FIX THIS!
                feature_cube[row][col][6] = 1.0
            if color_to_move == 'b':
                feature_cube[row][col][7] = 1.0
            else:
                assert color_to_move == 'w'
    return feature_cube


class BoardEvaluator:
    def __init__(self, tf_ckpt_path, board_size):
        # init the tensorflow model
        self.board_size = board_size
        self.ckpt_dir, _ = os.path.split(tf_ckpt_path)
        # TODO: here we need to specify the architecture of the CNN, this is not
        # what we want.
        self.model = CNNModel(board_size, layers=7, filters=64, ckpt_dir=self.ckpt_dir)

    # feature_cube - [board_size**2, 8] matrix of floats
    # returns - [board_size, board_size] matrix of probabilities
    def predict_single_sample(self, feature_cube):
        y_pred = self.model.sess.run(self.model.y_conv, feed_dict={self.model.x: [feature_cube]})
        return np.reshape(y_pred, [self.board_size, self.board_size])

    # board - GoBoard object
    # returns [board_size, board_size] matrix of floats, each float in [0,1] indicating
    # probability black owns the territory at the end of the game
    def evaluate_board(self, goBoard, color_to_move):
        feature_cube = _board_to_feature_cube(goBoard, color_to_move, self.board_size)
        predicted_ownership = self.predict_single_sample(feature_cube)

        # the model was trained on predicting ownership of color to move
        # here we swap this back to predicting ownership of black
        if color_to_move == "w":
            for i in range(len(predicted_ownership)):
                for j in range(len(predicted_ownership)):
                    predicted_ownership[i][j] = 1 - predicted_ownership[i][j]
        return predicted_ownership
