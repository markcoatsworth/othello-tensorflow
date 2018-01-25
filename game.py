from __future__ import print_function
from board import Board
from datetime import datetime
from random import randint
from randomgame import RandomGame

import copy
import numpy as np
import os
import time

BLACK = 1
WHITE = 2
GAME_OVER = 3
DRAW = 4


class Game(object):

    # [Game.init]
    # @description Constructor
    def __init__(self):
        self._board = Board()
        self._player_names = ["","",""]
        self._player_pieces = [[],[],[]]
        self._available_moves = [[],[],[]]
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

    # [Game.set_player_pieces]
    # @param1: Self
    # @param2: Player to set pieces for (1 or 2)
    # @return: Nothing. Set list of pieces, then exit.
    def set_player_pieces(self, player_num):
        pieces = []
        for i in range(64):
            if self._board._positions[i] == player_num:
                pieces.append(i)
        self._player_pieces[player_num] = pieces

    # [Game.set_available_moves]
    # @param1: Self
    # @param2: Player to set available moves for (1 or 2)
    # @return: Nothing. Set list of available moves, then exit.
    def set_available_moves(self, player_num):
        # MRC: Optimize this. The list of available moves should contain a series 
        # of pairs; each pair contains the index of the mov pos, along with a list
        # of all the directions the move can flip pieces along.
        moves = []
        for pos in range(64):
            if self._board.is_legal_move(player_num, pos):
                moves.append(pos)
        self._available_moves[player_num] = moves

    # [Game.generate_move]
    # @description Generates a (hopefully good) move for a player
    # @param1 Self
    # @param2 Player number to generate move for (1 or 2)
    def generate_move(self, player_num):

        opponent = player_num^3
        
        # Monte carlo simulations
        num_simulations = 500
        num_simulations_per_move = num_simulations // len(self._available_moves[player_num])
        monte_carlo_winners = []
        for move in self._available_moves[player_num]:
            this_move_winners = [0, 0, 0]
            for i in range(num_simulations_per_move):
                # Play a random game
                random_game = RandomGame()
                random_game._board = copy.deepcopy(self._board)
                random_game._board.play_move(player_num, move)
                this_move_winners[random_game.play(opponent, False)] += 1
            monte_carlo_winners.append([move, this_move_winners])

        # Determine which move won the most monte carlo simluations
        monte_carlo_best_move = [-1, -1]
        for move in monte_carlo_winners:
            if move[1][player_num] > monte_carlo_best_move[1]:
                monte_carlo_best_move = [move[0], move[1][player_num]]
        
        # For now, select move based on monte carlo simulations
        move_pos = monte_carlo_best_move[0]
        return move_pos


    # [Game.play]
    # @description: Main game loop. 
    # @param1: Self
    # @param2: Which player is human (BLACK or WHITE)
    def play(self, human_player):

        self._player_pieces[BLACK] = [28, 35]
        self._player_pieces[WHITE] = [27, 36]
        for p in self._player_pieces[BLACK]: self._board._positions[p] = BLACK
        for p in self._player_pieces[WHITE]: self._board._positions[p] = WHITE
        self.set_available_moves(BLACK)
        self.set_available_moves(WHITE)

        self._player_names[human_player] = "human"
        self._player_names[human_player^3] = "computer"

        # Main game loop
        while self._game_turn != GAME_OVER:

            current_player = self._game_turn
            opponent = self._game_turn^3
            
            self.set_player_pieces(BLACK)
            self.set_player_pieces(WHITE)
            self._board.show(self._available_moves[current_player])

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
                    print("Human played " + move_input + " (position " + str(move_pos) + ")\n")
                    self.set_available_moves(opponent)
                    # Check if other player passes, or if game is over
                    if len(self._available_moves[opponent]) == 0:
                        self.set_available_moves(current_player)
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
                start_time = datetime.now()
                move_pos = self.generate_move(current_player)
                self._board.play_move(current_player, move_pos)
                end_time = datetime.now()
                move_time = (end_time - start_time)

                print("Computer played " + str(chr((move_pos%8)+97)) + str((move_pos//8)+1) + " (position " + str(move_pos) + "), move took " + str(move_time) + "\n")
                self.set_available_moves(opponent)
                # Check if other player passes, or if game is over
                if len(self._available_moves[opponent]) == 0:
                    self.set_available_moves(current_player)
                    if len(self._available_moves[current_player]) == 0:
                        self._game_turn = GAME_OVER
                    else:
                        print("Computer has no available moves. Passing.")
                else:
                    self._game_turn = opponent

        # At this point we're out of the main loop, game is over! First
        print("\n\nGame over!\n")
        self._board.show(self._available_moves[human_player])
        self.set_player_pieces(BLACK)
        self.set_player_pieces(WHITE)
        print("Black has " + str(len(self._player_pieces[BLACK])) + " pieces")
        print("White has " + str(len(self._player_pieces[WHITE])) + " pieces\n")
        if len(self._player_pieces[BLACK]) > len(self._player_pieces[WHITE]):
            print("Black wins!\n\n")
        elif len(self._player_pieces[WHITE]) > len(self._player_pieces[BLACK]):
            print("White wins!\n\n")
        else:
            print("Game is a draw")
