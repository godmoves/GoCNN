# -*- coding: utf-8 -*-
import gomill.sgf
import numpy as np

from visualization.go_driver import GoDriver
from board_evaluation.pachi_player import Pachi


# set default board size.
BOARD_SIZE = 9

pachi = Pachi(pachi_path="thirdparty/pachi-pachi-12.10-jowa/pachi")
godriver = GoDriver("data/working/cnn_5layer_64filter", board_size=BOARD_SIZE)


def board_eval(sgf_content):
    pachi_matrix, score = pachi.get_final_score_matrix(sgf_content)
    assert len(pachi_matrix) == BOARD_SIZE ** 2
    pachi_matrix = np.array(pachi_matrix).reshape(BOARD_SIZE, BOARD_SIZE)

    # reset go board
    # skip komi, we will handle this later
    godriver.reset_board()
    try:
        sgf = gomill.sgf.Sgf_game.from_string(sgf_content)
    except ValueError:
        print('no SGF data found')
        return ''  # if this is not a sgf file, we return blank command
    sgf_iterator = sgf.main_sequence_iter()
    while True:
        try:
            it = sgf_iterator.next()
            color, move = it.get_move()
            if color is None:
                it = sgf_iterator.next()
                color, move = it.get_move()
        except StopIteration:
            break
        if move is not None:
            godriver.play(color, move)
    # scale the value range to [-1, 1]
    nn_matrix = godriver.evaluate_current_board() * 2 - 1
    final_matrix = 0.1 * nn_matrix + 0.9 * pachi_matrix

    # (0, 0) -> A1, (0, 8) ->I1, (8, 8)->I9
    return final_matrix
