#!/usr/bin/env python2
import numpy as np

from thirdparty.go_board import GoBoard
from visualization.board_evaluator import BoardEvaluator


def _swap_color(color):
    if color == "b":
        return "w"
    elif color == "w":
        return "b"
    raise ValueError("color needs to be w or b")


class GoDriver:
    '''
        GoDriver has a pointer to a gomill.Sgf_game object which contains the
        game tree defined by an sgf file. The current position in the file in
        maintained by the Sgf_game.main_sequence_iter() iterator. It also
        contains a BoardEvaluator object which will load the tensorflow model
        and be able to make predictions based on the current board.
    '''

    def __init__(self, tf_ckpt_path, board_size=19):
        self.board_evaluator = BoardEvaluator(tf_ckpt_path, board_size)
        self.board_size = board_size
        self.color_to_move = "b"

    def reset_board(self):
        self.board = GoBoard(self.board_size)
        self.color_to_move = "b"

    def play(self, color, move):
        if move != 'pass':
            (row, col) = move
            self.board.applyMove(color, (row, col))
        self.color_to_move = _swap_color(color)

    # returns [19,19] matrix of floats indicating the probability black will own
    # the territory at the end of the game
    def evaluate_current_board(self):
        if self.board is None:
            return np.zeros((self.board_size, self.board_size))
        return self.board_evaluator.evaluate_board(self.board, self.color_to_move)
