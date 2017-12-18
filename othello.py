#!/usr/bin/env python

from __future__ import print_function
from random import randint

import numpy as np
import os
import time

class Board(object):

    _board = [
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 2, 1, 0, 0, 0,
        0, 0, 0, 1, 2, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
    ]
    _weighted_board = [
        120, -20, 20,  5,   5,   20,  -20, 120,
        -20, -40, -5,  -5,  -5,  -5,  -40, -20,
        20,  -5,  15,  3,   3,   15,  -5,  20,
        5,   -5,  3,   3,   3,   3,   -5,  5,
        5,   -5,  3,   3,   3,   3,   -5,  5,
        20,  -5,  15,  3,   3,   15,  -5,  20,
        -20, -40, -5,  -5,  -5,  -5,  -40, -20,
        120, -20, 20,  5,   5,   20,  -20, 120
    ]

    # [Board.is_legal_move]
    # @param1: Self
    # @param2: Player number to play move for (1 or 2)
    # @param3: Board array positions to check (0 to 63)
    # @return: True if legal, False if not
    def is_legal_move(self, player_num, array_pos):
        
        if self._board[array_pos] != 0:
            return False

        # First, find all position indices adjacent to the move
        adjacent_positions=[ 
            (array_pos-9),  (array_pos-8),  (array_pos-7),
            (array_pos-1),                  (array_pos+1),
            (array_pos+7),  (array_pos+8),  (array_pos+9)
        ]
        # Trim invalid board spaces
        adjacent_positions = [x for x in adjacent_positions if (x >= 0 and x <= 63)]
        if array_pos % 8 == 0:
            adjacent_positions = [x for x in adjacent_positions if (x % 8 != 7)]
        elif array_pos % 8 == 7:
            adjacent_positions = [x for x in adjacent_positions if (x % 8 != 0)]

        # Now determine if any adjacent positions belong the the opponent
        for adj in adjacent_positions:
            if player_num + self._board[adj] == 3:
                # Traverse the board in the direction of the opponent piece
                # until we hit one of player_num's pieces (valid move) or we
                # hit an empty space or go off the board (invalid move)
                adj_diff =  adj - array_pos
                adj_traverse = array_pos + adj_diff
                # Watch out for the fucking edge of the board!
                while adj_traverse >= 0 and adj_traverse <= 63:
                    if self._board[adj_traverse] == 0:
                        break
                    elif self._board[adj_traverse] == player_num:
                        # Legal move! Return true.
                        return True
                    adj_traverse += adj_diff
                    

        # If we got to this point, it's not a legal move
        return False

    # [Board.get_player_pieces]
    # @param1: Self
    # @param2: Number of player to lookup pieces for (1 or 2)
    # @return: List of board positions
    def get_player_pieces(self, player_num):
        pieces = []
        for i in range(64):
            if self._board[i] == player_num:
                pieces.append(i)
        return pieces

    # [Board.get_available_moves]
    # @return: List of all legal, available moves for given player
    def get_available_moves(self, player_num):
        available_moves = []
        for pos in range(64):
            if self.is_legal_move(player_num, pos):
                available_moves.append(pos)
        return available_moves

    # [Board.play_move]
    # @description: Play a move, flip all necessary pieces. Important, we 
    #   assume the move is legal!
    # @param1: Self
    # @param2: Player number to play move for (1 or 2)
    # @param3: Move row (1 to 8)
    # @param4: Move column (1 to 8)
    def play_move(self, player_num, move_row, move_col):
        array_pos = (int(move_row)-1)*8 + (int(move_col)-1)

        # First, set the move position
        self._board[array_pos] = player_num

        # Now make a list of all adjacent positions
        adjacent_positions=[ 
            (array_pos-9),  (array_pos-8),  (array_pos-7),
            (array_pos-1),                  (array_pos+1),
            (array_pos+7),  (array_pos+8),  (array_pos+9)
        ]
        # Trim invalid board spaces
        adjacent_positions = [x for x in adjacent_positions if (x >= 0 and x <= 63)]
        if array_pos % 8 == 0:
            adjacent_positions = [x for x in adjacent_positions if (x % 8 != 7)]
        elif array_pos % 8 == 7:
            adjacent_positions = [x for x in adjacent_positions if (x % 8 != 0)]

        # Iterate over the adjacent positions, check for opponent pieces
        flip_pieces = []
        for adj in adjacent_positions:
            if player_num + self._board[adj] == 3:
                # Traverse the board in the direction of the opponent piece.
                # Keep track of all the position indicies on our path.
                adj_diff =  adj - array_pos
                adj_traverse = array_pos + adj_diff
                traverse_positions = []
                while adj_traverse >= 0 and adj_traverse <= 63:
                    # If we hit a 0 then opponent is not surrounded, bail out
                    if self._board[adj_traverse] == 0:
                        break
                    # Watch out for the left and right edges of the board!
                    # Need to make sure right/left and diagonal moves cannot
                    # cross the edges of the board, but up/down moves can run
                    # along left-most and right-most columns.
                    # The logic below is a disgusting mess. Try to clean it up?
                    if (adj_diff == 1 or adj_diff == 9) and adj_traverse % 8 == 7 and self._board[adj_traverse] != player_num:
                        break
                    elif (adj_diff == -1 or adj_diff == -9) and adj_traverse % 8 == 0 and self._board[adj_traverse] != player_num:
                        break
                    # Add surrounded opponent pieces to flip list. Don't flip
                    # them just yet, because they might influence other
                    # adjacent positions.
                    traverse_positions.append(adj_traverse)
                    if self._board[adj_traverse] == player_num:
                        for pos in traverse_positions:
                            flip_pieces.append(pos)
                        break
                    adj_traverse += adj_diff

        # Now we actually flip the surrounded pieces
        for pos in flip_pieces:
            self._board[pos] = player_num

    # [Board.show]
    # @description: Prints the board to stdout
    # @return: Nothing
    def show(self):
        for i in range(64):
            print(str(self._board[i]) + " ", end='')
            if (i % 8) == 7:
                print("")


class Game(object):

    _board = Board()
    _player1_pieces = _board.get_player_pieces(1)
    _player2_pieces = _board.get_player_pieces(2)
    _player1_available_moves = _board.get_available_moves(1)
    _player2_available_moves = _board.get_available_moves(2)

    # [Game.play]
    # @description: Main game play loop
    # @param1: Self
    # @param2: Starting player number (1 or 2)
    def play(self, start_player_num):

        game_state = "player" + str(start_player_num) + "_turn"

        # Main game loop
        while game_state != "game_over":

            self._board.show()
            self._player1_pieces = self._board.get_player_pieces(1)
            self._player2_pieces = self._board.get_player_pieces(2)
            print("\nPlayer 1 pieces: " + str(self._player1_pieces))
            print("Player 2 pieces: " + str(self._player2_pieces))
            print("Player 1 available moves: " + str(self._player1_available_moves))
            print("Player 2 available moves: " + str(self._player2_available_moves) + "\n")

            if game_state == "player1_turn":
                print("Player 1 (human) turn")
                move_row = raw_input("Row (1-8): ")
                move_col = raw_input("Col (1-8): ")

                if not move_row.isdigit() or not move_col.isdigit():
                    print("\n*** Invalid input! Try again ***\n")
                    time.sleep(1)
                    continue

                move_pos = (int(move_row)-1)*8 + (int(move_col)-1)
                if move_pos in self._player1_available_moves:
                    self._board.play_move(1, move_row, move_col)
                    print("Player 1 played at " + str(move_row) + ", " + str(move_col))
                    self._player2_available_moves = self._board.get_available_moves(2)
                    # Check if other player passes, or if game is over
                    if len(self._player2_available_moves) == 0:
                        self._player1_available_moves = self._board.get_available_moves(1)
                        if len(self._player1_available_moves) == 0:
                            game_state = "game_over"
                        else:
                            print("Player 2 has no available moves. Passing.")
                    else:
                        game_state = "player2_turn"
                else:
                    print("\n*** Invalid move! Try again ***\n")
                    time.sleep(1)

            elif game_state == "player2_turn":
                # For now, computer plays a random move
                move_row = randint(1, 8)
                move_col = randint(1, 8)
                move_pos = (int(move_row)-1)*8 + (int(move_col)-1)
                while move_pos not in self._player2_available_moves:
                    move_row = randint(1, 8)
                    move_col = randint(1, 8)
                    move_pos = (int(move_row)-1)*8 + (int(move_col)-1)
                self._board.play_move(2, move_row, move_col)
                print("Computer played at row " + str(move_row) + ", column " + str(move_col) + "\n")
                self._player1_available_moves = self._board.get_available_moves(1)
                # Check if other player passes, or if game is over
                if len(self._player1_available_moves) == 0:
                    self._player2_available_moves = self._board.get_available_moves(2)
                    if len(self._player2_available_moves) == 0:
                        game_state = "game_over"
                    else:
                        print("Player 1 has no available moves. Passing.")
                else:
                    game_state = "player1_turn"

        # At this point we're out of the main loop, game is over! First
        print("\n\nGame over!\n")
        print("Player 1 has " + str(len(self._player1_pieces)) + " pieces")
        print("Player 2 has " + str(len(self._player2_pieces)) + " pieces\n")
        if len(self._player1_pieces) > len(self._player2_pieces):
            print("Player 1 wins!\n\n")
        elif len(self._player2_pieces) > len(self._player1_pieces):
            print("Player 2 wins!\n\n")
        else:
            print("Game is a draw")



def main():
    game = Game()
    game.play(2)

if __name__ == "__main__":
    main()