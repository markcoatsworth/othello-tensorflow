#!/usr/bin/env python

from __future__ import print_function
from board import Board
from random import randint

import numpy as np
import os
import time

BLACK = 1
WHITE = 2
GAME_OVER = 3
DRAW = 4

class RandomGame(object):

    def __init__(self):
        self._board = Board()
        self._player_names = ["","Black","White"]
        self._player_pieces = [[],[],[]]
        self._available_moves = [[],[],[]]

    # [RandomGame.set_player_pieces]
    # @param1: Self
    # @param2: Player to set pieces for (1 or 2)
    # @return: Nothing. Set list of pieces, then exit.
    def set_player_pieces(self, player_num):
        pieces = []
        for i in range(64):
            if self._board._positions[i] == player_num:
                pieces.append(i)
        self._player_pieces[player_num] = pieces

    # [RandomGame.set_available_moves]
    # @param1: Self
    # @param2: Player to set available moves for (1 or 2)
    # @return: Nothing. Set list of available moves, then exit.
    def set_available_moves(self, player_num):
        moves = []
        for pos in range(64):
            if self._board.is_legal_move(player_num, pos):
                moves.append(pos)
        self._available_moves[player_num] = moves
    
    # [Game.play]
    # @description: Main game loop. 
    # @param1: Self
    # @param2: Play who moves first
    def play(self, start_player, verbose=False):

        self.set_available_moves(BLACK)
        self.set_available_moves(WHITE)
        self._game_turn = start_player

        # Main game loop
        while self._game_turn != GAME_OVER:

            current_player = self._game_turn
            opponent = self._game_turn^3
            
            self.set_player_pieces(BLACK)
            self.set_player_pieces(WHITE)

            if verbose:
                self._board.show(self._available_moves[current_player])
                print("\nBlack pieces: " + str(self._player_pieces[BLACK]))
                print("White pieces: " + str(self._player_pieces[WHITE]))
                print("Black available moves: " + str(self._available_moves[BLACK]))
                print("White available moves: " + str(self._available_moves[WHITE]) + "\n")

            # Current player plays a random move
            move_pos = self._available_moves[current_player][np.random.randint(0, len(self._available_moves[current_player]))]
            self._board.play_move(current_player, move_pos)
            if verbose:
                print(str(self._player_names[current_player]) + " played " + str(chr((move_pos%8)+97)) + str((move_pos//8)+1) + " (position " + str(move_pos) + ")\n")
            self.set_available_moves(opponent)
            # Check if other player passes, or if game is over
            if len(self._available_moves[opponent]) == 0:
                self.set_available_moves(current_player)
                if len(self._available_moves[current_player]) == 0:
                    self._game_turn = GAME_OVER
            else:
                self._game_turn = opponent

        # At this point we're out of the main loop, game is over!
        self.set_player_pieces(BLACK)
        self.set_player_pieces(WHITE)
        if verbose:
            self._board.show(self._available_moves[current_player])
            print("Black has " + str(len(self._player_pieces[BLACK])) + " pieces")
            print("White has " + str(len(self._player_pieces[WHITE])) + " pieces\n")
        if len(self._player_pieces[BLACK]) > len(self._player_pieces[WHITE]):
            return BLACK
        elif len(self._player_pieces[WHITE]) > len(self._player_pieces[BLACK]):
            return WHITE
        else:
            return DRAW