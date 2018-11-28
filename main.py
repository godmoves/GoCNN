#!/usr/bin/env python2
import argparse
import sys
import json

from munge.data_preprocessor import munge_all_sgfs
from board_evaluation.train import nn_trainer
from visualization.GTP import gtp_io
from data.download_data import download_cgos_data


def mode_download(parser):
    parser.add_argument('download', help='mode download')
    parser.add_argument('--save_path', dest='save_path', type=str,
                        default='./data/raw', help='path to save all data files')
    args = parser.parse_args()
    download_cgos_data(args.save_path)


def mode_preprocess(parser):
    parser.add_argument('preprocess', help='preprocess mode')
    parser.add_argument('-i', '--input_dir', dest='input_dir', type=str,
                        default='./data/raw', help='directory containing sgf files as inputk')
    parser.add_argument('-o', '--output_dir', dest='output_dir', type=str,
                        default='./data/input', help='output directory to write processed binary files to')
    parser.add_argument('-c', '--completed_dir', dest='completed_dir', default='./data/gnugo',
                        help='directory to save gnugo completed sgf files (with ownership info)')
    parser.add_argument('-b', '--board_size', dest='board_size', type=int,
                        default=9, help='board size')
    parser.add_argument('--no_ownership', dest='ownership', default=True,
                        action='store_false', help='do not count ownership')

    args = parser.parse_args()
    params = vars(args)
    print(json.dumps(params, indent=2))

    input_dir = params["input_dir"]
    output_dir = params["output_dir"]
    completed_dir = params["completed_dir"]
    board_size = params["board_size"]
    ownership = params["ownership"]

    munge_all_sgfs(input_dir, output_dir, completed_dir, board_size, ownership)


def mode_train(parser):
    parser.add_argument('train', help='train mode')
    parser.add_argument('--train_dir', dest='train_dir', type=str,
                        default='./data/input/train', help='directory contains training data')
    parser.add_argument('--test_dir', dest='test_dir', type=str,
                        default='./data/input/test', help='directory contains test data')
    parser.add_argument('-b', '--board_size', dest='board_size', type=int,
                        default=9, help='board size')
    parser.add_argument('--ckpt_path', dest='ckpt_path', type=str,
                        default='./data/working/test.ckpt', help='path to check point')

    args = parser.parse_args()
    params = vars(args)
    print(json.dumps(params, indent=2))

    train_dir = params['train_dir']
    test_dir = params['test_dir']
    ckpt_path = params['ckpt_path']
    board_size = params["board_size"]

    nn_trainer(train_dir, test_dir, ckpt_path, board_size, total_steps=1500)


def mode_gtp(parser):
    parser.add_argument('gtp', help='gtp mode')
    parser.add_argument('--model_path', dest='model_path', type=str,
                        default='./data/working/test.ckpt',
                        help='path to tensorflow model')
    parser.add_argument('-b', '--board_size', dest='board_size', type=int,
                        default=9, help='board size')
    args = parser.parse_args()
    params = vars(args)

    model_path = params['model_path']
    board_size = params["board_size"]

    gtp_io(model_path, board_size)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    help_str = 'Using command:\n  python main.py [mode] [args]\n  '\
               'Check specific args in each mode by `python main.py [mode] -h`\n'

    try:
        mode = sys.argv[1]
    except IndexError:
        print(help_str)
        raise ValueError('please specify a running mode: [download, preprocess, train, gtp]')

    if mode == 'download':
        mode_download(parser)
    elif mode == 'preprocess':
        mode_preprocess(parser)
    elif mode == 'train':
        mode_train(parser)
    elif mode == 'gtp':
        mode_gtp(parser)
    elif mode in ['help', '-h', '--help']:
        print(help_str)
    else:
        raise NotImplementedError("Mode [%s] not implemented" % mode)
