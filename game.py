from __future__ import print_function
from anytree import Node, RenderTree
from board import Board
from datetime import datetime
from random import randint
from randomgame import RandomGame

import copy
import numpy as np
import os
import time
import timeit

BLACK = 1
WHITE = 2
GAME_OVER = 3
DRAW = 4

# Game tunings
MINMAX_DEPTH = 1
MONTE_CARLO_NUM_SIMULATIONS = 10000


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
        moves = []
        for pos in range(64):
            if self._board.is_legal_move(player_num, pos):
                moves.append(pos)
        self._available_moves[player_num] = moves

    # [Game.build_minmax_tree]
    # @param1: Self
    # @param2: Player who we are currently evaluating moves for (1 or 2)
    # @param3: Available moves for this player
    # @param4: Parent node in the minmax tree
    # @param5: Current depth
    def build_minmax_tree(self, player_num, available_moves, parent_move, parent_game, depth):
        # Base case
        if depth == 0:
            return

        # Recursive case: minmax lookahead
        opponent = player_num^3
        for move in available_moves:

            # Setup a new minmax game based on the recursive board state. Play the
            # move, then reevaluate player pieces + opponent available moves
            minmax_game = Game()
            minmax_game = copy.deepcopy(parent_game)
            minmax_game._board.play_move(player_num, move)
            minmax_game.set_player_pieces(BLACK)
            minmax_game.set_player_pieces(WHITE)
            minmax_game.set_available_moves(opponent)

            # If MINMAX_DEPTH is odd, we calculate for player_num on odd depths
            # who then becomes opponent at even depths, and vice versa.
            if depth % 2 == MINMAX_DEPTH % 2:
                move_score = minmax_game._board.evaluate_score(player_num, minmax_game._player_pieces)
                #print("[build_minmax_tree] depth=" + str(depth) + ", calculating score for player_num=" + str(player_num) + ", move=" + str(move) + ", move_score=" + str(move_score) + ", minmax_game._player_pieces=" + str(minmax_game._player_pieces))
            else:
                move_score = minmax_game._board.evaluate_score(opponent, minmax_game._player_pieces)
                #print("[build_minmax_tree] depth=" + str(depth) + ", calculating score for opponent=" + str(opponent) + ", move=" + str(move) + ", move_score=" + str(move_score) + ", minmax_game._player_pieces=" + str(minmax_game._player_pieces))
            node_score = [move, move_score]
            this_move = Node(node_score, parent=parent_move)
            #print("[Game.build_minmax_tree] move=" + str(move) + ", this_move=" + str(this_move) + ", move_score=" + str(move_score) + ", minmax_game._player_pieces[player_num]=" + str(minmax_game._player_pieces[player_num])+ ", minmax_game._player_pieces[opponent]=" + str(minmax_game._player_pieces[opponent]))
            self.build_minmax_tree(opponent, minmax_game._available_moves[opponent], this_move, minmax_game, depth-1)

    # [Game.get_minmax_results]
    # @description: Evaluate the minmax tree, give results for all available moves
    # @param1: Self
    # @return: A list of all currently available moves, paired with a score for each
    def get_minmax_results(self):
        # Evaluate the tree, make min/max adjustments
        self.evaluate_minmax_tree(self._minmax_tree)
        # Return the results of the top level.
        results = []
        for child in self._minmax_tree.children:
            results.append(child.name)
        return results

    # [Game.evaluate_minmax_tree]
    # @description: Recursively roll up the minmax tree
    def evaluate_minmax_tree(self, parent, depth=0):
        # Base case
        if not parent.children:
            return
        else:
            for child in parent.children:
                #print("[Game.evaluate_minmax_tree] depth=" + str(depth) + ", parent=" + str(parent) + ", child=" + str(child))
                self.evaluate_minmax_tree(child, depth+1)
                
                # Scan children for min value
                if depth % 2 == 1:
                    #print("[Game.evaluate_minmax_tree] depth=ODD, parent.name=" + str(parent.name) + ", looking for min value, child.name=" + str(child.name) + ", child.name[1]=" + str(child.name[1]))
                    if parent.name[1] > child.name[1]:
                        parent.name[1] = child.name[1]
                        #print("[Game.evaluate_minmax_tree] At depth=" + str(depth) + ", adjusting parent to new min-value, parent=" + str(parent))
                # Scan children for max value
                else:
                    #print("[Game.evaluate_minmax_tree] depth=EVEN, parent.name=" + str(parent.name) + ", looking for max value, child.name=" + str(child.name) + ", child.name[1]=" + str(child.name[1]))
                    if parent.name[1] < child.name[1]:
                        parent.name[1] = child.name[1]
                        #print("[Game.evaluate_minmax_tree] At depth=" + str(depth) + ", adjusting parent to new max-value, parent=" + str(parent))



    # [Game.generate_move]
    # @description Generates a (hopefully good) move for a player
    # @param1 Self
    # @param2 Player number to generate move for (1 or 2)
    def generate_move(self, player_num):
        
        # Build a new minmax tree and get results for all nodes
        self._minmax_tree = Node("root")
        self.build_minmax_tree(player_num, self._available_moves[player_num], self._minmax_tree, self, MINMAX_DEPTH)
        print(RenderTree(self._minmax_tree))
        minmax_results = self.get_minmax_results()
        print("[generate_move] minmax_results=" + str(minmax_results))

        # Monte carlo simulations
        num_simulations_per_move = MONTE_CARLO_NUM_SIMULATIONS // len(self._available_moves[player_num])
        monte_carlo_results = []
        opponent = player_num^3
        for move in self._available_moves[player_num]:
            this_move_results = [0, 0, 0]
            for i in range(num_simulations_per_move):
                # Play a random game
                random_game = RandomGame()
                random_game._board = copy.deepcopy(self._board)
                random_game._board.play_move(player_num, move)
                this_move_results[random_game.play(opponent, False)] += 1
            monte_carlo_results.append([move, this_move_results])

        # Evaluate confidence of minmax results
        minmax_confidence = {}
        minmax_total_score = 0
        minmax_min_result = 0
        # Adjust all results to be >= 0
        for result in minmax_results:
            #minmax_total_score += result[1]
            if result[1] < minmax_min_result:
                minmax_min_result = result[1]
        if minmax_min_result < 0:
            for result in minmax_results:
                result[1] -= (minmax_min_result - 1)
        for result in minmax_results:
            minmax_total_score += result[1]
        minmax_average_score = float(minmax_total_score) / float(len(minmax_results))
        for result in minmax_results:
            this_result_confidence = float(result[1]) / float(minmax_average_score)
            #print("[generate_move] minmax_average_score=" + str(minmax_average_score) + ", result[1]=" + str(result[1]) + ", this_result_confidence=" + str(this_result_confidence))
            minmax_confidence[result[0]] = this_result_confidence
        print("[generate_move] minmax_confidence=" + str(minmax_confidence))
        
        # Evaluate confidence of monte carlo simulations
        monte_carlo_confidence = {}
        for result in monte_carlo_results:
            this_result_confidence = float(result[1][player_num])/float(num_simulations_per_move)
            monte_carlo_confidence[result[0]] = this_result_confidence
        print("[generate_move] monte_carlo_confidence=" + str(monte_carlo_confidence))

        # Evaluate total confidence of available moves
        moves_confidence = []
        for move in self._available_moves[player_num]:
            this_move_confidence = minmax_confidence[move] * monte_carlo_confidence[move]
            moves_confidence.append([move, this_move_confidence])
        print("[generate_move] moves_confidence=" + str(moves_confidence))
        
        # Choose a best move based on maximum confidence
        best_move = moves_confidence[0][0]
        best_move_confidence = moves_confidence[0][1]
        for move in moves_confidence:
            if move[1] > best_move_confidence:
                best_move = move[0]
                best_move_confidence = move[1]

        # Play a random move
        #move_pos = self._available_moves[player_num][np.random.randint(0, len(self._available_moves[player_num]))]

        return best_move

    # [Game.generate_move_alt]
    # @description Generates an alternate (hopefully good) move for a player.
    #   Used for robot battles to try different strategies.
    # @param1 Self
    # @param2 Player number to generate move for (1 or 2)
    def generate_move_alt(self, player_num):
        
        # Build a new minmax tree and get results for all nodes
        self._minmax_tree = Node("root")
        self.build_minmax_tree(player_num, self._available_moves[player_num], self._minmax_tree, self, 3)
        print(RenderTree(self._minmax_tree))
        minmax_results = self.get_minmax_results()
        #print("[generate_move_alt] minmax_results=" + str(minmax_results))

        # Monte carlo simulations
        num_simulations_per_move = MONTE_CARLO_NUM_SIMULATIONS // len(self._available_moves[player_num])
        monte_carlo_results = []
        opponent = player_num^3
        for move in self._available_moves[player_num]:
           this_move_results = [0, 0, 0]
           for i in range(num_simulations_per_move):
               # Play a random game
               random_game = RandomGame()
               random_game._board = copy.deepcopy(self._board)
               random_game._board.play_move(player_num, move)
               this_move_results[random_game.play(opponent, False)] += 1
           monte_carlo_results.append([move, this_move_results])

        # Evaluate confidence of minmax results
        minmax_confidence = {}
        minmax_total_score = 0
        minmax_min_result = 0
        # Adjust all results to be >= 0
        for result in minmax_results:
            #minmax_total_score += result[1]
            if result[1] < minmax_min_result:
                minmax_min_result = result[1]
        if minmax_min_result < 0:
            for result in minmax_results:
                result[1] -= (minmax_min_result - 1)
        for result in minmax_results:
            minmax_total_score += result[1]
        minmax_average_score = float(minmax_total_score) / float(len(minmax_results))
        for result in minmax_results:
            this_result_confidence = float(result[1]) / float(minmax_average_score)
            #print("[generate_move_alt] minmax_average_score=" + str(minmax_average_score) + ", result[1]=" + str(result[1]) + ", this_result_confidence=" + str(this_result_confidence))
            minmax_confidence[result[0]] = this_result_confidence
        print("[generate_move_alt] minmax_confidence=" + str(minmax_confidence))
        
        # Evaluate confidence of monte carlo simulations
        monte_carlo_confidence = {}
        for result in monte_carlo_results:
            this_result_confidence = float(result[1][player_num])/float(num_simulations_per_move)
            monte_carlo_confidence[result[0]] = this_result_confidence
        print("[generate_move_alt] monte_carlo_confidence=" + str(monte_carlo_confidence))

        # Evaluate total confidence of available moves
        moves_confidence = []
        for move in self._available_moves[player_num]:
            this_move_confidence = minmax_confidence[move] * monte_carlo_confidence[move]
            moves_confidence.append([move, this_move_confidence])
        print("[generate_move_alt] moves_confidence=" + str(moves_confidence))
        
        # Choose a best move based on maximum confidence
        best_move = moves_confidence[0][0]
        best_move_confidence = moves_confidence[0][1]
        for move in moves_confidence:
            if move[1] > best_move_confidence:
                best_move = move[0]
                best_move_confidence = move[1]

        # Play a random move
        #move_pos = self._available_moves[player_num][np.random.randint(0, len(self._available_moves[player_num]))]

        return best_move


    # [Game.play_human]
    # @description: Human vs computer main game loop
    # @param1: Self
    # @param2: Which player is human (BLACK or WHITE)
    def play_human(self, human_player):

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
                move_input = raw_input("Human move [a-h][1-8]: ")
                
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
                print("Computer is thinking...\n")
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

    # [Game.robot_battle]
    # @description: Computer vs computer main game loop. Use this to test
    #   different strategies and board weightings.
    # @param1: Self
    def robot_battle(self, verbose=True):
        self._player_pieces[BLACK] = [28, 35]
        self._player_pieces[WHITE] = [27, 36]
        for p in self._player_pieces[BLACK]: self._board._positions[p] = BLACK
        for p in self._player_pieces[WHITE]: self._board._positions[p] = WHITE
        self.set_available_moves(BLACK)
        self.set_available_moves(WHITE)

        self._player_names[BLACK] = "Black"
        self._player_names[WHITE] = "White"
        self._game_turn = BLACK

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

            # Current player plays a move. BLACK player tries new experimental
            # features.
            start_time = datetime.now()
            if current_player == BLACK:
                move_pos = self.generate_move_alt(current_player)
            else:
                move_pos = self.generate_move(current_player)
            self._board.play_move(current_player, move_pos)
            end_time = datetime.now()
            move_time = (end_time - start_time)
            
            if verbose:
                print("\n" + (str(self._player_names[current_player])) + " played " + str(chr((move_pos%8)+97)) + str((move_pos//8)+1) + " (position " + str(move_pos) + "), move took " + str(move_time) + "\n")
            self.set_available_moves(opponent)
            # Check if other player passes, or if game is over
            if len(self._available_moves[opponent]) == 0:
                self.set_available_moves(current_player)
                if len(self._available_moves[current_player]) == 0:
                    self._game_turn = GAME_OVER
            else:
                self._game_turn = opponent

        # At this point we're out of the main loop, game is over! First
        print("\n\nGame over!\n")
        self._board.show(self._available_moves[current_player])
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
