#!/usr/bin/env python2

# this file contains methods with call gnugo to finish games from sgf files
# (remove dead stones) after removing dead stones we can easily determine final
# board ownership

import re
import os
import threading
from subprocess import PIPE, Popen

import gomill.sgf
import numpy as np

from thirdparty.go_board import GoBoard


def finish_sgf(sgf_filepath, dest_file, board_size=19, difference_threshold=6,
               year_lowerbound=0, gnugo_timeout=10, lower_move_limit=70):
    '''
        gnugo will write the resutls to dest_file returns True if successful and
        False if something went wrong

        sgf_filepath - str, path to the sgf file we need to complete
    '''

    sgf_file = open(sgf_filepath, 'r')
    contents = sgf_file.read()
    sgf_file.close()

    move_count = contents.count(";")

    # I added this to speed up the process. Many files in the dataset were
    # incomplete games, even though the final score was recorded. gnugo would
    # take a long time to finish these incomplete games.
    if move_count < lower_move_limit:
        print("%s only had %d moves" % (sgf_filepath, move_count))
        return False

    if contents.find('SZ[%d]' % board_size) < 0:
        print('not %dx%d, skipping: %s' % (board_size, board_size, sgf_filepath))
        return False

    valid, score = parse_sgf_result(sgf_filepath, contents, board_size)
    if not valid:
        return False

    # check the date of the game and skip if it is too old
    match_str = r"DT\[([0-9]+)"
    m = re.search(match_str, contents)
    if m:
        year = int(m.group(1))
        if year < year_lowerbound:
            print("Game is too old: %s" % sgf_filepath)
            return False

    gnugo_path = os.path.join(os.getcwd(), "thirdparty/gnugo-3.8/interface/gnugo")
    output = run_gungo(gnugo_path, sgf_filepath, dest_file)

    if output == "Jigo\n":
        gnu_score = 0
    else:
        m = re.search(r"([A-Za-z]+) wins by ([0-9\.]+) points", output)
        if m is None:
            return False
        winner = m.group(1)
        gnu_score = float(m.group(2))
        if winner == "White":
            gnu_score *= -1

    if np.abs(score - gnu_score) > difference_threshold and board_size > 9:
        print("GNU messed up finishing this game... removing %s" % dest_file)
        os.remove(dest_file)
        return False
    return True


def parse_sgf_result(sgf_filepath, contents, board_size=19):
    # we first determine the recorded score in the sgf file, this can be compared
    # with what gnugo determines the score to be

    # for small board size we reserve all games
    if board_size <= 9:
        return True, 0

    match_str = r'RE\[([a-zA-Z0-9_\+\.]+)\]'
    m = re.search(match_str, contents)
    if m:
        result_str = m.group(1)
        # handle draw for cgos rule
        if result_str == 'Draw':
            score = 0
        else:
            pieces = result_str.split("+")
            try:
                winner = pieces[0]
                if pieces[1] == "" or pieces[1][0].lower() == "r" or pieces[1][0].lower() == "t":
                    print("Skipping because result was: %s" % result_str)
                    return False, 0
                score = float(pieces[1])
                if winner == "W":
                    score *= -1
            except Exception:
                print("Error parsing result, result_str = %s, file: %s" % (result_str, sgf_filepath))
                return False, 0
    else:
        print("Couldn't find result, skipping: %s" % sgf_filepath)
        return False, 0
    return True, score


def run_gungo(gnugo_path, sgf_filepath, dest_file):
    # we call gnugo with the appropriate flags to finish the game. gnugo will
    # write the results to dest_file
    p = Popen([gnugo_path, "-l", sgf_filepath, "--outfile", dest_file,
               "--score", "aftermath", "--capture-all-dead",
               "--chinese-rules"], stdout=PIPE)
    timer = threading.Timer(10, p.kill)
    try:
        timer.start()
        # gnugo will print the final score, we check this with whats written in
        # the sgffile
        output, err = p.communicate()
    finally:
        timer.cancel()

    print(output)
    return output


def get_final_ownership(gnu_sgf_outputfile, board_size=19):
    '''
        we parse this file and get the final state of the board from it. Seki
        positions both groups are considered alive and we randomly assign the
        spaces between seki groups

        gnu_sgf_outputfile - str, filepath to the file gnugo output
    '''
    sgffile = open(gnu_sgf_outputfile, 'r')
    sgfContents = sgffile.read()
    sgffile.close()

    sgf = gomill.sgf.Sgf_game.from_string(sgfContents)

    if sgf.get_size() != board_size:
        print('boardsize not %d, ignoring' % board_size)
        return

    board = GoBoard(board_size)
    for move in sgf.root.get_setup_stones()[0]:
        board.applyMove("b", move)
    for move in sgf.root.get_setup_stones()[1]:
        board.applyMove("w", move)

    moveIdx = 0
    for it in sgf.main_sequence_iter():
        (color, move) = it.get_move()
        if color is not None and move is not None:
            (row, col) = move
            board.applyMove(color, (row, col))
            moveIdx = moveIdx + 1

    black_ownership = board.get_final_ownership('b')
    white_ownership = np.zeros((board_size, board_size))
    for i in range(len(white_ownership)):
        for j in range(len(white_ownership)):
            if black_ownership[i][j] == 0:
                white_ownership[i][j] = 1
            else:
                white_ownership[i][j] = 0

    return black_ownership, white_ownership


def finish_sgf_and_get_ownership(sgf_file_path, sgf_file_name, completed_dir,
                                 board_size=19, difference_threshold=6,
                                 year_lowerbound=0):
    dest_file = os.path.join(completed_dir, sgf_file_name) + "c"

    # first we check if gnugo has already finished this game, if so we just open
    # the .sfgc file can grab final ownership if we haven't munged already, munge
    # it now. munging may fail if gnugo believes final score is more the
    # difference_threshold away.
    if not os.path.exists(dest_file):
        if not(finish_sgf(sgf_file_path, dest_file, board_size,
                          difference_threshold, year_lowerbound)):
            return None, None  # failed to finish the game
    else:
        print("gnugo has already finished %s" % dest_file)
    black_ownership, white_ownership = get_final_ownership(dest_file, board_size)
    return black_ownership, white_ownership


def traverse_directory(source_dir_path, dest_dir_path):
    file_count = 0
    for subdir, dirs, files in os.walk(source_dir_path):
        for file in files:
            filepath = os.path.join(subdir, file)
            if filepath.endswith(".sgf"):
                print(file_count)
                try:
                    finish_sgf(filepath, file, dest_dir_path)
                except Exception:
                    print("Uncaught exception for %s" % filepath)
                file_count += 1
    print("There were %d files" % (file_count))
