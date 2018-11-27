#!/usr/bin/env python2

'''
This file contains the main loop which communicates to gogui via the Go Text Protocol (gtp) via stdin.
We start by loading a random sgf file contained in the SGF_DIRECTORY. You can walk through
the sgf file by clicking the 'make board_evaluator play' button in gogui. Everytime the
loadsgf command is sent from gogui (Tools -> Analyze Commands in gogui) we load
a new random sgf from the directory. When the predict ownership method is called
we return the models board evaluation prediction on the current state of the board.
'''

from __future__ import print_function
import sys
import re
import random
import numpy as np
import os
from GoDriver import GoDriver


letter_coords = "ABCDEFGHJKLMNOPQRST"


# sgf_dir - string, directory containing sgf files
# returns list of strings
def get_sgf_filelist(sgf_dir):
    print("Looking for games in %s" % sgf_dir, file=sys.stderr)
    sgf_files = []
    for subdir, dirs, files in os.walk(sgf_dir):
        for file in files:
            filepath = os.path.join(subdir, file)
            if filepath.endswith(".sgf"):
                sgf_files.append(filepath)
    print("Number of sgf files found: %d" % len(sgf_files), file=sys.stderr)
    return sgf_files


# go from matrix index to board position string e.g. 0,2 -> A3
def coord_to_str(row, col):
    # return letter_coords[row] + str(col + 1)
    return letter_coords[col] + str(row + 1)


# ownership_matrix - [board_size, board_size] matrix of floats output from the CNN model
# Formats a valid response string that can be fed into gogui as response to the
# 'predict_ownership' command
def influence_str(ownership_matrix):
    print("Score without komi: %.2f" % np.sum(2 * ownership_matrix - 1), file=sys.stderr)
    rtn_str = "INFLUENCE "
    for i in range(len(ownership_matrix)):
        for j in range(len(ownership_matrix)):
            # convert to [-1,1] scale
            rtn_str += "%s %.1lf " % (coord_to_str(i, j), 2 * (ownership_matrix[i][j] - .5))
            # rtn_str+= " %.1lf\n" %(ownership_matrix[i][j])
    return rtn_str


def gtp_io(sgf_dir, model_path, board_size):
    """ Main loop which communicates to gogui via GTP"""
    known_commands = ['boardsize', 'clear_board', 'komi', 'play', 'genmove',
                      'final_score', 'quit', 'name', 'version', 'known_command',
                      'list_commands', 'protocol_version', 'gogui-analyze_commands']
    analyze_commands = ["gfx/Predict Final Ownership/predict_ownership",
                        "none/Load New SGF/loadsgf"]
    sgf_files = get_sgf_filelist(sgf_dir)
    sgf_file = random.choice(sgf_files)
    driver = GoDriver(sgf_file, model_path, board_size=board_size)

    print("starting main.py: loading %s" % sgf_file, file=sys.stderr)
    output_file = open("output.txt", "wb")
    output_file.write("intializing\n")
    while True:
        try:
            line = raw_input().strip()
            print(line, file=sys.stderr)
            output_file.write(line + "\n")
        except EOFError:
            output_file.write('Breaking!!\n')
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
        elif command[0] == "loadsgf":
            sgf_file = random.choice(sgf_files)
            print("Loading new file: %s" % sgf_file, file=sys.stderr)
            print("Make sure to click 'Clear board and start new game' in the gui", file=sys.stderr)
            driver.load_sgf_file(sgf_file)
        elif command[0] == "komi":
            pass
        elif command[0] == "play":
            pass
            print("play", file=sys.stderr)
        elif command[0] == "genmove":
            # color_str = command[1] #currently we ignore this
            tup = driver.gen_move()
            if tup == "pass":
                ret = "pass"
            else:
                ret = coord_to_str(tup[0], tup[1])
            print("genmove", file=sys.stderr)
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
            output_file.write("returning: '=%s %s'\n" % (cmdid, ret,))
            print('=%s %s\n\n' % (cmdid, ret,), end='')
        else:
            output_file.write("returning: '=?%s ???'\n" % (cmdid))
            print('?%s ???\n\n' % (cmdid,), end='')
        sys.stdout.flush()
    output_file.write('end of session\n')
    output_file.close()
