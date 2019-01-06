# -*- coding: utf-8 -*-
import xlrd
import time

import pandas
import gomill.sgf
import numpy as np

from visualization.go_driver import GoDriver
from board_evaluation.pachi_player import Pachi


# set default board size.
BOARD_SIZE = 9

pachi = Pachi(pachi_path="thirdparty/pachi-pachi-12.10-jowa/pachi")
godriver = GoDriver("data/working/cnn_5layer_64filter", board_size=BOARD_SIZE)


def board_eval(sgf_content):
    # reset go board
    # skip komi, we will handle this later
    godriver.reset_board()
    try:
        sgf = gomill.sgf.Sgf_game.from_string(sgf_content)
    except ValueError:
        print('WARNING: no SGF data found')
        # if this is not a sgf file, we return blank command
        return np.zeros((BOARD_SIZE, BOARD_SIZE))
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

    # pachi player is used to reinforcement the neural network
    pachi_matrix, score = pachi.get_final_score_matrix(sgf_content)
    if pachi_matrix is None:
        pachi_matrix = nn_matrix
    else:
        assert len(pachi_matrix) == BOARD_SIZE ** 2
        pachi_matrix = np.array(pachi_matrix).reshape(BOARD_SIZE, BOARD_SIZE)

    final_matrix = 0.1 * nn_matrix + 0.9 * pachi_matrix

    # (0, 0) -> A1, (0, 8) ->I1, (8, 8)->I9
    return final_matrix


if __name__ == '__main__':
    # readbook = xlrd.open_workbook("./data/kifu_test/test9x9.xlsx")
    # sheet = readbook.sheet_by_index(0)
    # start_time = time.time()
    # for i in range(sheet.nrows):
    #     sgf_content = sheet.cell(i, 3).value.encode('utf-8')
    #     try:
    #         score = board_eval(sgf_content)
    #         print("sgf id {} score {}".format(i, np.sum(score)))
    #     except Exception as e:
    #         print("sgf id {} exception {}".format(i, e))
    #     if i % 100 == 0:
    #         print("time used: {}s".format(time.time() - start_time))

    sql = pandas.read_csv("./data/kifu_test/test_sql.csv")
    sgfs = sql["Sgf"]
    print("sgf nums {}".format(sgfs.size))
    start_time = time.time()
    for i, f in enumerate(sgfs):
        sgf_content = f.encode('utf-8')
        try:
            score = board_eval(sgf_content)
            print("sgf id {} score {}".format(i, np.sum(score)))
        except Exception as e:
            print("sgf id {} exception {}".format(i, e))
        if i % 100 == 0:
            print("time used: {}s".format(time.time() - start_time))
