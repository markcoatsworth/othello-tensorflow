#!/usr/bin/env python

from __future__ import print_function
from board import Board
from random import randint

import numpy as np
import os
import time

GAME_OVER = 0
BLACK = 1
WHITE = 2


class Game(object):

    _board = Board()
    _black_pieces = _board.get_player_pieces(BLACK)
    _white_pieces = _board.get_player_pieces(WHITE)
    _black_available_moves = _board.get_available_moves(BLACK)
    _white_available_moves = _board.get_available_moves(WHITE)

    # [Game.play]
    # @description: Main game loop. 
    # @param1: Self
    # @param2: Starting player (BLACK or WHITE)
    def play(self, start_player):

        self._game_turn = start_player

        # Main game loop
        while self._game_turn != GAME_OVER:

            self._board.show()
            self._black_pieces = self._board.get_player_pieces(BLACK)
            self._white_pieces = self._board.get_player_pieces(WHITE)

            print("\nBlack pieces: " + str(self._black_pieces))
            print("White pieces: " + str(self._white_pieces))
            print("Black available moves: " + str(self._black_available_moves))
            print("White available moves: " + str(self._white_available_moves) + "\n")

            if self._game_turn == BLACK:
                print("Black turn")
                move_col = input("Col (a-h): ")
                move_row = input("Row (1-8): ")

                if not move_row.isdigit() or not move_col.isdigit():
                    print("\n*** Invalid input! Try again ***\n")
                    time.sleep(1)
                    continue

                move_pos = (int(move_row)-1)*8 + (int(move_col)-1)
                if move_pos in self._black_available_moves:
                    self._board.play_move(BLACK, move_row, move_col)
                    print("Black played at " + str(move_row) + ", " + str(move_col))
                    self._white_available_moves = self._board.get_available_moves(WHITE)
                    # Check if other player passes, or if game is over
                    if len(self._white_available_moves) == 0:
                        self._black_available_moves = self._board.get_available_moves(BLACK)
                        if len(self._black_available_moves) == 0:
                            self._game_turn = GAME_OVER
                        else:
                            print("White has no available moves. Passing.")
                    else:
                        self._game_turn = "white_turn"
                else:
                    print("\n*** Invalid move! Try again ***\n")
                    time.sleep(1)

            elif self._game_turn == WHITE:
                # For now, computer plays a random move
                move_col = randint(1, 8)
                move_row = randint(1, 8)
                move_pos = (int(move_row)-1)*8 + (int(move_col)-1)
                while move_pos not in self._white_available_moves:
                    move_row = randint(1, 8)
                    move_col = randint(1, 8)
                    move_pos = (int(move_row)-1)*8 + (int(move_col)-1)
                self._board.play_move(WHITE, move_row, move_col)
                print("White played at row " + str(move_row) + ", column " + str(move_col) + "\n")
                self._white_available_moves = self._board.get_available_moves(BLACK)
                # Check if other player passes, or if game is over
                if len(self._black_available_moves) == 0:
                    self._white_available_moves = self._board.get_available_moves(WHITE)
                    if len(self._white_available_moves) == 0:
                        self._game_turn = GAME_OVER
                    else:
                        print("White has no available moves. Passing.")
                else:
                    self._game_turn = BLACK

        # At this point we're out of the main loop, game is over! First
        print("\n\nGame over!\n")
        self._board.show()
        self._black_pieces = self._board.get_player_pieces(BLACK)
        self._white_pieces = self._board.get_player_pieces(WHITE)
        print("Black has " + str(len(self._black_pieces)) + " pieces")
        print("White has " + str(len(self._white_pieces)) + " pieces\n")
        if len(self._black_pieces) > len(self._white_pieces):
            print("Black wins!\n\n")
        elif len(self._white_pieces) > len(self._black_pieces):
            print("White wins!\n\n")
        else:
            print("Game is a draw")



def main():
    game = Game()
    game.play(WHITE)

if __name__ == "__main__":
    main()