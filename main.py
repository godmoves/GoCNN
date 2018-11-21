#!/usr/bin/env python2

import argparse
import sys
import json

from munge.data_preprocessor import munge_all_sgfs


def mode_preprocess(parser):
    # settings for munging
    parser.add_argument('preprocess',
                        help='preprocess mode')
    parser.add_argument('-i', '--input_dir',
                        dest='input_dir',
                        type=str,
                        default='./data/raw',
                        help='directory containing sgf files as inputk')
    parser.add_argument('-o', '--output_dir',
                        dest='output_dir',
                        type=str,
                        default='./data/input',
                        help='output directory to write processed binary files to')
    parser.add_argument('-c', '--completed_dir',
                        dest='completed_dir',
                        default='./data/gnugo',
                        help='directory to save gnugo completed sgf files (with ownership info)')
    parser.add_argument('-b', '--board_size',
                        dest='board_size',
                        type=int,
                        default=9,
                        help='board size')
    parser.add_argument('--no_ownership',
                        dest='ownership',
                        default=True,
                        action='store_false',
                        help='do not count ownership')

    args = parser.parse_args()
    params = vars(args)
    print(json.dumps(params, indent=2))

    input_dir = params["input_dir"]
    output_dir = params["output_dir"]
    completed_dir = params["completed_dir"]
    board_size = params["board_size"]
    ownership = params["ownership"]

    munge_all_sgfs(input_dir, output_dir, completed_dir, board_size, ownership)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    mode = sys.argv[1]
    if mode == 'preprocess':
        mode_preprocess(parser)
    else:
        raise NotImplementedError("Mode [%s] not implemented" % mode)
