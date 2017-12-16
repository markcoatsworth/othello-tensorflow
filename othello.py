#!/usr/bin/env python

from __future__ import print_function
from random import randint

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

    def __init__(self, value=None):
        print("Initializing game board...")

    # [Board.is_legal_move]
    # @return: True if legal, False if not
    def is_legal_move(self, player_num, move_row, move_col):
        array_pos = (int(move_row)-1)*8 + int(move_col)-1
        
        if self._board[array_pos] != 0:
            return False

        # First, find all position indices adjacent to the move
        adjacent_indexes=[ 
            (array_pos-9),  (array_pos-8),  (array_pos-7),
            (array_pos-1),                  (array_pos+1),
            (array_pos+7),  (array_pos+8),  (array_pos+9)
        ]

        # Only copy valid positions (between 0 and 63) to our adjacency list
        adjacent_positions=[]
        for index in adjacent_indexes:
            if index >= 0 and index <= 63:
                adjacent_positions.append(index)

        # Now determine if any adjacent positions belong the the opponent
        for adj in adjacent_positions:
            if player_num + self._board[adj] == 3:
                # Traverse the board in the direction of the opponent piece
                # until we hit one of player_num's pieces (valid move) or we
                # hit an empty space or go off the board (invalid move)
                adj_diff =  adj - array_pos
                adj_traverse = array_pos + adj_diff
                while self._board[adj_traverse] != 0 and adj_traverse >= 0 and adj_traverse <= 63:
                    adj_traverse += adj_diff
                    if self._board[adj_traverse] == player_num:
                        # Legal move! Return true.
                        return True

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
        return []

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

        # Now make a list of all adjacent, valid indices
        adjacent_indexes=[ 
            (array_pos-9),  (array_pos-8),  (array_pos-7),
            (array_pos-1),                  (array_pos+1),
            (array_pos+7),  (array_pos+8),  (array_pos+9)
        ]
        adjacent_positions=[]
        for index in adjacent_indexes:
            if index >= 0 and index <= 63:
                adjacent_positions.append(index)

        # Iterate over the adjacent positions, check for opponent pieces
        for adj in adjacent_positions:
            if player_num + self._board[adj] == 3:
                # Traverse the board in the direction of the opponent piece.
                # Keep track of all the position indicies on our path.
                adj_diff =  adj - array_pos
                adj_traverse = array_pos + adj_diff
                traverse_positions = []
                while self._board[adj_traverse] != 0 and adj_traverse >= 0 and adj_traverse <= 63:
                    traverse_positions.append(adj_traverse)
                    adj_traverse += adj_diff
                    # Flip all surrounded opponent positions
                    if self._board[adj_traverse] == player_num:
                        for pos in traverse_positions:
                            self._board[pos] = player_num


    def show(self):
        for i in range(64):
            print(str(self._board[i]) + " ", end='')
            if (i % 8) == 7:
                print("")


def main():
    
    board = Board()
    
    # Setup the initial game state
    player1_pieces=board.get_player_pieces(1)
    player2_pieces=board.get_player_pieces(2)
    player1_available_moves=board.get_available_moves(1)
    player2_available_moves=board.get_available_moves(2)
    game_state = "player1_turn"

    while game_state != "game_over":

        board.show()
        print("Player 1 pieces: " + str(player1_pieces))
        print("Player 2 pieces: " + str(player2_pieces))
        print("Player 1 available moves: " + str(player1_available_moves))
        print("Player 2 available moves: " + str(player2_available_moves) + "\n")

        if game_state == "player1_turn":
            print("Player 1 (human) turn")
            move_row = raw_input("Row (1-8): ")
            move_col = raw_input("Col (1-8): ")
            if board.is_legal_move(1, move_row, move_col):
                board.play_move(1, move_row, move_col)
                print("Player 1 played at " + str(move_row) + ", " + str(move_col))
                game_state = "player2_turn"
            else:
                print("\n*** Invalid move! Try again ***\n")
                time.sleep(1)
        
        elif game_state == "player2_turn":
            # For now, computer plays a random move
            move_row = randint(1, 8)
            move_col = randint(1, 8)
            while board.is_legal_move(2, move_row, move_col) == False:
                move_row = randint(1, 8)
                move_col = randint(1, 8)
            board.play_move(2, move_row, move_col)
            print("Computer played at " + str(move_row) + ", " + str(move_col))
            game_state = "player1_turn"


if __name__ == "__main__":
    main()