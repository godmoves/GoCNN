#!/usr/bin/python

# Copyright Hugh Perkins 2015 hughperkins at gmail
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.

# assumptions:
# - at least python 2.7
# - not python 3.x
# - internet is available
# - on linux (since we're using signals)

# Note this file was modified from Hugh Perkins kgsgo_dataset_preprocessor
# library. I added in functionality to call gnugo in order to determine the
# final state of the board (remove dead stones, fill in dame, etc.) and changed
# how it traverses directories.

# See main at bottom of file. This file will recursively traverse a directory for
# all .sgf files and convert the moves in those games to a binary format which
# can be used downstream for a CNN.

from __future__ import absolute_import
from __future__ import division

import sys
import os

import gomill
import gomill.sgf
import pandas as pd

from munge import finish_games
from munge import bit_writer
from thirdparty import GoBoard


def addToDataFile(datafile, color, move, goBoard, ownership, black_ownership, white_ownership, board_size):
    '''
        datafile is an open binary file we are writing to
        color is the color of the next person to move
        move is the move they decided to make
        goBoard represents the state of the board before they moved, object GoBoard
        black ownership is a 19x19 array where 1 indicates black owns the
            intersection at the end of the game, 0 indicates otherwise. white
            ownership is same matrix but flipped

        - we should flip the board and color so we are basically always black
        - we should calculate liberties at each position
        - we should get ko
        - and we should write to the file :-)

        planes we should write:
        0: our stones with 1 liberty
        1: our stones with 2 liberty
        2: our stones with 3 or more liberties
        3: their stones with 1 liberty
        4: their stones with 2 liberty
        5: their stones with 3 or more liberty
        6: simple ko
        7: color to move, 1 for black and 0 for white
        8: all ones...
    '''

    (row, col) = move
    enemyColor = goBoard.otherColor(color)
    datafile.write('GO')  # write something first, so we can sync/validate on reading
    datafile.write(chr(row))  # write the move
    datafile.write(chr(col))

    # If we are doing ownership, write the final state of the board as sequential bits
    if ownership:
        if color == 'b':
            to_move_ownership = black_ownership
        elif color == 'w':
            to_move_ownership = white_ownership

        flattened_targets = [to_move_ownership[i][j] for i in range(board_size) for j in range(board_size)]
        bit_writer.write_sequence(flattened_targets, datafile)

    # The 8 board feature planes are encoded by sequential bytes, one byte per position on the board
    for row in range(0, goBoard.boardSize):
        for col in range(0, goBoard.boardSize):
            thisbyte = 0
            pos = (row, col)
            if goBoard.board.get(pos) == color:
                if goBoard.goStrings[pos].liberties.size() == 1:
                    thisbyte = thisbyte | 1
                elif goBoard.goStrings[pos].liberties.size() == 2:
                    thisbyte = thisbyte | 2
                else:
                    thisbyte = thisbyte | 4
            if goBoard.board.get(pos) == enemyColor:
                if goBoard.goStrings[pos].liberties.size() == 1:
                    thisbyte = thisbyte | 8
                elif goBoard.goStrings[pos].liberties.size() == 2:
                    thisbyte = thisbyte | 16
                else:
                    thisbyte = thisbyte | 32
            if goBoard.isSimpleKo(color, pos):
                thisbyte = thisbyte | 64
            # if color == 'b':  # mark the color to move
            #     thisbyte = thisbyte | 128
            thisbyte = thisbyte | 128
            datafile.write(chr(thisbyte))


def walkthroughSgf(sgf_contents, sgf_file_path, sgf_file_name, output_file_path,
                   completed_dir, board_size, ownership):
    '''
        walk through the sgf file and write the binary samples to output_file_path

        sgfContects - str with the contents of the sgf file to parse
        sgf_file_path - str, path to the sgf file
        output_file_path - str, path to the output file
    '''
    sgf = gomill.sgf.Sgf_game.from_string(sgf_contents)
    try:
        if sgf.get_size() != board_size:
            print('boardsize not %d, ignoring' % board_size)
            return
        goBoard = GoBoard.GoBoard(board_size)
        if sgf.get_handicap() is not None and sgf.get_handicap() != 0:
            print('handicap not zero, ignoring (' + str(sgf.get_handicap()) + ')')
            return
    except Exception:
        print("Error getting handicap. Ignoring this file")
        return
    moveIdx = 0

    # here we attempt to use gnugo to finish the game and get the final ownership.
    # we check the score gnugo gives with the score written in the file, if this
    # score is off by more than difference_threshold then we skip the file. gnugo
    # is often off by 1 because of chinese scoring.
    black_ownership, white_ownership = None, None
    if ownership:
        # set year_lowerbound will ignore all games before given year
        black_ownership, white_ownership = finish_games.finish_sgf_and_get_ownership(
            sgf_file_path, sgf_file_name, completed_dir, board_size,
            difference_threshold=6, year_lowerbound=0)

        if black_ownership is None or white_ownership is None:
            print("Unable to get final ownership for %s" % sgf_file_path)
            return

    # all samples from this sgf will be written to this file
    output_file = open(output_file_path, 'wb')

    for it in sgf.main_sequence_iter():
        (color, move) = it.get_move()
        if color is not None and move is not None:
            (row, col) = move
            addToDataFile(output_file, color, move, goBoard, ownership, black_ownership,
                          white_ownership, board_size)
            try:
                goBoard.applyMove(color, (row, col))
            except Exception:
                print("exception caught at move %d" % (moveIdx))
                print("Ignoring the rest of this file")
                output_file.close()
                return
            moveIdx = moveIdx + 1
    output_file.close()


def munge_sgf(sgf_file_path, sgf_file_name, output_file_path, completed_dir, board_size, ownership):
    '''
        open the sgf file, read the contents and write them to the binary file output_file_path

        sgf_file_path - str, path to the sgf file
        sgf_file_name - str, name of the sgf file (without the entire path)
        output_file_path - str, path to the output file
    '''
    sgf_file = open(sgf_file_path, 'r')
    contents = sgf_file.read()
    sgf_file.close()

    if contents.find('SZ[%d]' % board_size) < 0:
        print('not %dx%d, skipping: %s' % (board_size, board_size, sgf_file_path))
    try:
        walkthroughSgf(contents, sgf_file_path, sgf_file_name, output_file_path,
                       completed_dir, board_size, ownership)
    except Exception:
        print("Weird exception happened caught for file " + os.path.abspath(sgf_file_path))
        print(sys.exc_info()[0])
        # os.remove(sgf_file_path)
        # print "Terminating the munging..."
        # raise


def munge_csv(file_path, file_name, file_count, output_file_path_base, completed_dir, board_size, ownership):
    file = pd.read_csv(file_path)
    for content in file['sgf']:
        output_file_path = output_file_path_base + str(file_count) + '.dat'
        walkthroughSgf(content, file_path, file_name, output_file_path, completed_dir, board_size, ownership)
        file_count += 1

    return file_count


def munge_all_sgfs(input_dir, output_dir, completed_dir, board_size, ownership):
    '''
        recursively traverse the source_dir directory and process every .sgf
        file in that directory. We ignore all files that are not board_sizexboard_size,
        and skip handicap games. The GoGod dataset I downloaded had a few corrupted
        sgf files, these will be skipped as well.
    '''
    file_count = 0
    for subdir, dirs, files in os.walk(input_dir):
        for file in files:
            filepath = os.path.join(subdir, file)
            if file_count % 1000 == 0:
                print('file count: %d' % file_count)
            if filepath.endswith(".sgf"):
                output_file_path = os.path.join(output_dir, file[:-4]) + ".dat"
                if os.path.isfile(output_file_path):
                    print("File already exists: %s" % output_file_path)
                    continue
                munge_sgf(filepath, file, output_file_path, completed_dir, board_size, ownership)
                file_count += 1
            # elif filepath.endswith(".csv"):
            #     output_file_path_base = os.path.join(output_dir, file[:-4]) + '_'
            #     if os.path.isfile(output_file_path_base):
            #         print("File already exists: %s" % output_file_path_base)
            #         continue
            #     file_count = munge_csv(filepath, file, file_count, output_file_path_base,
            #                            completed_dir, board_size, ownership)
    print("There were %d files" % (file_count))
    if file_count == 0:
        print("No sgf_files were found in the directory, nothing to do.")
    else:
        if not os.path.exists(output_dir):
            print("%s not found, creating it" % output_dir)
            os.mkdir(output_dir)
        if not os.path.exists(completed_dir):
            print("%s not found, creating it" % completed_dir)
            os.mkdir(completed_dir)
