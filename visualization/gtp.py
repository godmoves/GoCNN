#!/usr/bin/env python2

'''
This file contains the main loop which communicates to gogui via the Go Text Protocol (gtp) via stdin.
When the predict ownership method is called we return the models board evaluation prediction on the
current state of the board.
'''

from __future__ import print_function
import sys
import re

import numpy as np

from visualization.go_driver import GoDriver


letter_coords = "ABCDEFGHJKLMNOPQRST"


# go from matrix index to board position string e.g. 0,2 -> A3
def coord_to_str(row, col):
    return letter_coords[col] + str(row + 1)


def str_to_coord(move):
    row = int(move[1:]) - 1
    col = letter_coords.index(move[0].upper())
    return (row, col)


# ownership_matrix - [board_size, board_size] matrix of floats output from the CNN model
# Formats a valid response string that can be fed into gogui as response to the
# 'predict_ownership' command
def influence_str(ownership_matrix):
    score = np.sum(2 * ownership_matrix - 1) - 7
    print("Score (komi=7): %.2f" % score, file=sys.stderr)
    rtn_str = "INFLUENCE "
    for i in range(len(ownership_matrix)):
        for j in range(len(ownership_matrix)):
            # convert to [-1,1] scale
            rtn_str += "%s %.1lf " % (coord_to_str(i, j), 2 * (ownership_matrix[i][j] - .5))
            # rtn_str+= " %.1lf\n" %(ownership_matrix[i][j])
    return rtn_str


def gtp_io(model_path, board_size):
    """ Main loop which communicates to gogui via GTP"""
    known_commands = ['boardsize', 'clear_board', 'komi', 'play', 'list_commands',
                      'final_score', 'quit', 'name', 'version', 'known_command',
                      'protocol_version', 'gogui-analyze_commands']
    analyze_commands = ["gfx/Predict Final Ownership/predict_ownership"]
    driver = GoDriver(model_path, board_size=board_size)

    while True:
        try:
            line = raw_input().strip()
            print(line, file=sys.stderr)
        except EOFError:
            break
        if line == '':
            continue
        command = [s.lower() for s in line.split()]
        if re.match('\d+', command[0]):
            cmdid = command[0]
            command = command[1:]
        else:
            cmdid = ''
        ret = ''
        if command[0] == "boardsize":
            if int(command[1]) != board_size:
                print("Warning: Trying to set incompatible boardsize %s (!= %d)" % (
                      command[1], board_size), file=sys.stderr)
        elif command[0] == "clear_board":
            driver.reset_board()
        elif command[0] == "komi":
            pass
        elif command[0] == "play":
            color = command[1][0]
            move = command[2]
            if move != 'pass':
                (row, col) = str_to_coord(move)
                driver.play(color, (row, col))
            else:
                driver.play(color, move)
            print(str(driver.board), file=sys.stderr)
        elif command[0] == "final_score":
            print("final_score not implemented", file=sys.stderr)
        elif command[0] == "name":
            ret = 'board_evaluator'
        elif command[0] == "predict_ownership":
            ownership_prediction = driver.evaluate_current_board()
            ret = influence_str(ownership_prediction)
        elif command[0] == "version":
            ret = '1.0'
        elif command[0] == "list_commands":
            ret = '\n'.join(known_commands)
        elif command[0] == "gogui-analyze_commands":
            ret = '\n'.join(analyze_commands)

        elif command[0] == "known_command":
            ret = 'true' if command[1] in known_commands else 'false'
        elif command[0] == "protocol_version":
            ret = '2'
        elif command[0] == "quit":
            print('=%s \n\n' % (cmdid,), end='')
            break
        else:
            print('Warning: Ignoring unknown command - %s' % (line,), file=sys.stderr)
            ret = None

        if ret is not None:
            print('=%s %s\n\n' % (cmdid, ret,), end='')
        else:
            print('?%s ???\n\n' % (cmdid,), end='')
        sys.stdout.flush()
