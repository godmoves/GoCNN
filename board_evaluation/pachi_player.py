#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from subprocess import Popen, PIPE

import gomill
import gomill.sgf
import gomill.common


class Pachi():
    def __init__(self, pachi_path):
        self.pachi_path = pachi_path
        self.count = 0
        self.pachi = Popen([self.pachi_path], shell=True, stdin=PIPE,
                           stdout=PIPE, stderr=PIPE)

    def build_pachi_cmd(self, sgf_content):
        try:
            sgf = gomill.sgf.Sgf_game.from_string(sgf_content)
        except ValueError:
            print('no SGF data found')
            return ''  # if this is not a sgf file, we return blank command
        sgf_iterator = sgf.main_sequence_iter()
        pachi_cmd = 'boardsize 9\n'
        pachi_cmd += 'clear_board\n'
        # default komi is 7.5
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
        # restart pachi after 50 evaluations, this can avoid pachi get stuck
        if (self.count >= 40):
            self.restart()
            self.count = 0
        else:
            self.count += 1
        pachi_cmd = self.build_pachi_cmd(sgf_content)
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

    def get_final_score_matrix(self, sgf_content):
        influence, score = self.get_final_score(sgf_content)
        influence_matrix = map(float, influence.split()[2:][1::2])
        return influence_matrix, score

    def restart(self):
        self.pachi.kill()
        self.pachi = Popen([self.pachi_path], shell=True, stdin=PIPE,
                           stdout=PIPE, stderr=PIPE)
