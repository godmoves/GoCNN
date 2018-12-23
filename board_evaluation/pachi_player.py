#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import xlrd
import gomill
import gomill.sgf
import gomill.common
from subprocess import Popen, PIPE
import sys


# we need to set the default coding to utf-8 to read Chinese characters
reload(sys)
sys.setdefaultencoding('utf-8')


class Pachi():
    def __init__(self, pachi_path):
        self.pachi_path = pachi_path
        self.pachi = Popen([self.pachi_path], shell=True, stdin=PIPE,
                           stdout=PIPE, stderr=PIPE)

    def get_pachi_cmd(self, sgf_content):
        try:
            sgf = gomill.sgf.Sgf_game.from_string(sgf_content)
        except ValueError:
            print('no SGF data found')
            return ''  # if this is not a sgf file, we return blank command
        sgf_iterator = sgf.main_sequence_iter()
        pachi_cmd = 'boardsize 9\n'
        pachi_cmd += 'clear_board\n'
        pachi_cmd += 'komi 7.5\n'
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
                pachi_cmd += 'play {} {}\n'.format(
                    color.upper(), gomill.common.format_vertex(move))

        pachi_cmd += 'gogui-ownermap\n'
        return pachi_cmd

    def parse_score(self, score):
        if score is None:
            return score
        sign = -1 if 'W' in score else 1
        abs_score = float(score.split('+')[1])
        return sign * abs_score

    def get_final_score(self, sgf_content):
        pachi_cmd = self.get_pachi_cmd(sgf_content)
        self.pachi.stdin.write(pachi_cmd)
        self.pachi.stdin.flush()
        influence, score = None, None
        # we will wait for result while the command is not blank
        while pachi_cmd is not '':
            line = self.pachi.stdout.readline().decode('utf-8')
            if 'INFLUENCE' in line:
                influence = line
            if 'TEXT' in line:
                score = line
                break

        score = self.parse_score(score)
        return influence, score

    def restart(self):
        self.pachi.kill()
        self.pachi = Popen([self.pachi_path], shell=True, stdin=PIPE,
                           stdout=PIPE, stderr=PIPE)


# pachi = Pachi('/home/mankit/Work/go/pachi/pachi')
# readbook = xlrd.open_workbook('test9x9.xlsx')
# sheet = readbook.sheet_by_index(0)

# nrows, ncols = sheet.nrows, sheet.ncols
# print('Rows: {} Cols: {}'.format(nrows, ncols))

# for i in range(nrows):
#     sgf_content = str(sheet.cell(i, 3).value)
#     _, score = pachi.get_final_score(sgf_content)
#     print('game {}, score {}'.format(i + 1, score))
#     if i % 50 == 0:
#         pachi.restart()
