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


class Game(object):

    _board = Board()
    # Cheap hack to allow empty board pieces to retain value 0: add an extra
    # empty list at index 0, so both indices 1 (BLACK) and 2 (WHITE) are valid.
    _player_names = ["","",""]
    _player_pieces = [[],[],[]]
    _available_moves = [[],[],[]]
    
    # [Game.init]
    # @description Constructor
    def __init__(self):
        self._available_moves[BLACK] = self._board.get_available_moves(BLACK)
        self._available_moves[WHITE] = self._board.get_available_moves(WHITE)
        self._game_turn = BLACK

    # [Game.is_valid_input]
    # @description: Verify that an input string matches [a-h][1-8] format
    def is_valid_input(self, input):
        if not len(str(input)) == 2:
            return False
        move_col = ord(input[0]) - 96
        if str.isdigit(input[1]):
            move_row = int(input[1])
        else:
            return False
        if not ((move_col >= 1 and move_col <= 8) and (move_row >= 1 and move_row <= 8)):
            return False
        return True


    # [Game.play]
    # @description: Main game loop. 
    # @param1: Self
    # @param2: Which player is human (BLACK or WHITE)
    def play(self, human_player):

        self._player_names[human_player] = "human"
        self._player_names[human_player^3] = "computer"

        # Main game loop
        while self._game_turn != GAME_OVER:

            self._board.show()
            self._player_pieces[BLACK] = self._board.get_player_pieces(BLACK)
            self._player_pieces[WHITE] = self._board.get_player_pieces(WHITE)
            
            current_player = self._game_turn
            opponent = self._game_turn^3

            print("\nBlack (" + self._player_names[BLACK] + ") pieces: " + str(self._player_pieces[BLACK]))
            print("White (" + self._player_names[WHITE] + ") pieces: " + str(self._player_pieces[WHITE]))
            print("Black (" + self._player_names[BLACK] + ") available moves: " + str(self._available_moves[BLACK]))
            print("White (" + self._player_names[WHITE] + ") available moves: " + str(self._available_moves[WHITE]) + "\n")

            # Human turn
            if current_player == human_player:
                move_input = input("Human move [a-h][1-8]: ")
                
                if not self.is_valid_input(move_input):
                    print("\n*** Invalid input! Try again ***\n")
                    time.sleep(1)
                    continue

                move_pos = (int(int(move_input[1]))-1)*8 + (int(ord(move_input[0])-96)-1)

                if move_pos in self._available_moves[current_player]:
                    self._board.play_move(current_player, move_pos)
                    print("Human played " + move_input + " pos=" + str(move_pos))
                    self._available_moves[opponent] = self._board.get_available_moves(opponent)
                    # Check if other player passes, or if game is over
                    if len(self._available_moves[opponent]) == 0:
                        self._available_moves[current_player] = self._board.get_available_moves(current_player)
                        if len(self._available_moves[current_player]) == 0:
                            self._game_turn = GAME_OVER
                        else:
                            print("Human has no available moves. Passing.")
                    else:
                        self._game_turn = opponent
                else:
                    print("\n*** Invalid move! Try again ***\n")
                    time.sleep(1)

            # Computer turn
            else:
                # For now, computer plays a random move
                move_pos = self._available_moves[current_player][randint(0, len(self._available_moves[current_player])-1)]
                self._board.play_move(current_player, move_pos)
                print("Computer played at pos " + str(move_pos) + "\n")
                self._available_moves[opponent] = self._board.get_available_moves(opponent)
                # Check if other player passes, or if game is over
                if len(self._available_moves[opponent]) == 0:
                    self._available_moves[current_player] = self._board.get_available_moves(current_player)
                    if len(self._available_moves[current_player]) == 0:
                        self._game_turn = GAME_OVER
                    else:
                        print("Computer has no available moves. Passing.")
                else:
                    self._game_turn = opponent

        # At this point we're out of the main loop, game is over! First
        print("\n\nGame over!\n")
        self._board.show()
        self._player_pieces[BLACK] = self._board.get_player_pieces(BLACK)
        self._player_pieces[WHITE] = self._board.get_player_pieces(WHITE)
        print("Black has " + str(len(self._player_pieces[BLACK])) + " pieces")
        print("White has " + str(len(self._player_pieces[WHITE])) + " pieces\n")
        if len(self._player_pieces[BLACK]) > len(self._player_pieces[WHITE]):
            print("Black wins!\n\n")
        elif len(self._player_pieces[WHITE]) > len(self._player_pieces[BLACK]):
            print("White wins!\n\n")
        else:
            print("Game is a draw")



def main():
    game = Game()
    game.play(WHITE)

if __name__ == "__main__":
    main()