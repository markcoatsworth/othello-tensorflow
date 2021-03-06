import copy
import numpy as np

BLACK = 1
WHITE = 2

class Board(object):

    def __init__(self):
        self._positions = np.zeros(64, np.int8)
        self._weighted_positions = np.zeros(shape=(3, 64), dtype=int)
        self._weighted_positions[BLACK] = [
            120, -20, 20,  5,   5,   20,  -20, 120,
            -20, -40, -5,  -5,  -5,  -5,  -40, -20,
            20,  -5,  15,  3,   3,   15,  -5,  20,
            5,   -5,  3,   3,   3,   3,   -5,  5,
            5,   -5,  3,   3,   3,   3,   -5,  5,
            20,  -5,  15,  3,   3,   15,  -5,  20,
            -20, -40, -5,  -5,  -5,  -5,  -40, -20,
            120, -20, 20,  5,   5,   20,  -20, 120
        ]
        self._weighted_positions[WHITE] = [
            120, -20, 20,  5,   5,   20,  -20, 120,
            -20, -40, -5,  -5,  -5,  -5,  -40, -20,
            20,  -5,  15,  3,   3,   15,  -5,  20,
            5,   -5,  3,   3,   3,   3,   -5,  5,
            5,   -5,  3,   3,   3,   3,   -5,  5,
            20,  -5,  15,  3,   3,   15,  -5,  20,
            -20, -40, -5,  -5,  -5,  -5,  -40, -20,
            120, -20, 20,  5,   5,   20,  -20, 120
        ]
        self._adjacent_positions = []
        self.set_adjacent_positions()

    # [Board.set_adjacent_positions]
    # @description: Fills the _adjacent_positions array, so we can later look
    #   up all adjacent positions to any index in constant time.
    def set_adjacent_positions(self):
        for pos in range(0, 64):
            adj_pos=[ 
                (pos-9),  (pos-8),  (pos-7),
                (pos-1),            (pos+1),
                (pos+7),  (pos+8),  (pos+9)
            ]
            # Trim invalid board spaces
            adj_pos = [x for x in adj_pos if (x >= 0 and x <= 63)]
            if pos % 8 == 0:
                adj_pos = [x for x in adj_pos if (x % 8 != 7)]
            elif pos % 8 == 7:
                adj_pos = [x for x in adj_pos if (x % 8 != 0)]
            # Now insert this into the master list
            self._adjacent_positions.insert(pos, adj_pos)

    # [Board.evaluate_score]
    # @description: EValuate the game board score based on weightings
    # @param1: Self
    # @param2: Player number to calculate score for (1 or 2)
    def evaluate_score(self, player_num, player_pieces):
        opponent = player_num^3
        player_score = 0
        for pos in player_pieces[player_num]:
            player_score += self._weighted_positions[player_num][pos]
        
        opponent_score = 0
        for pos in player_pieces[opponent]:
            opponent_score += self._weighted_positions[opponent][pos]
        
        score = player_score - opponent_score
        return score

    # [Board.is_legal_move]
    # @param1: Self
    # @param2: Player number to play move for (1 or 2)
    # @param3: Board array positions to check (0 to 63)
    # @return: True if legal, False if not
    def is_legal_move(self, player_num, array_pos):
        
        if self._positions[array_pos] != 0:
            return False

        adjacent_positions = self._adjacent_positions[array_pos]

        # Now determine if any adjacent positions belong the the opponent
        for adj in adjacent_positions:
            if player_num + self._positions[adj] == 3:
                # Traverse the board in the direction of the opponent piece
                # until we hit one of player_num's pieces (valid move) or we
                # hit an empty space or go off the board (invalid move)
                adj_diff =  adj - array_pos
                adj_traverse = array_pos + adj_diff

                # Watch out for the edge of the board!
                while adj_traverse >= 0 and adj_traverse <= 63:
                    if self._positions[adj_traverse] == 0:
                        break
                    # Block moves that cross over the right side of the board
                    if adj_diff in [-7, 1, 9] and adj_traverse % 8 == 7 and self._positions[adj_traverse] != player_num:
                        break
                    # Block moves that cross over the left side of the board
                    elif adj_diff in [-9, -1, 7] and adj_traverse % 8 == 0 and self._positions[adj_traverse] != player_num:
                        break
                    if self._positions[adj_traverse] == player_num:
                        # Legal move! Return true.
                        return True
                    adj_traverse += adj_diff

        # If we got to this point, it's not a legal move
        return False

    # [Board.play_move]
    # @description: Play a move, flip all necessary pieces. Important, we 
    #   assume the move is legal!
    # @param1: Self
    # @param2: Player number to play move for (1 or 2)
    # @param3: Move position (0 to 63)
    def play_move(self, player_num, move_pos):
        
        # Set the move position, get list of adjacent positions
        self._positions[move_pos] = player_num
        adjacent_positions = self._adjacent_positions[move_pos]

        # Iterate over the adjacent positions, check for opponent pieces
        flip_pieces = []
        for adj in adjacent_positions:
            if player_num + self._positions[adj] == 3:
                # Traverse the board in the direction of the opponent piece.
                # Keep track of all the position indicies on our path.
                adj_diff =  adj - move_pos
                adj_traverse = move_pos + adj_diff
                traverse_positions = []
                while adj_traverse >= 0 and adj_traverse <= 63:
                    # If we hit a 0 then opponent is not surrounded, bail out
                    if self._positions[adj_traverse] == 0:
                        break
                    # Block moves that cross over the right side of the board
                    if adj_diff in [-7, 1, 9] and adj_traverse % 8 == 7 and self._positions[adj_traverse] != player_num:
                        break
                    # Block moves that cross over the left side of the board
                    elif adj_diff in [-9, -1, 7] and adj_traverse % 8 == 0 and self._positions[adj_traverse] != player_num:
                        break
                    # Add surrounded opponent pieces to flip list. Don't flip
                    # them just yet, because they might influence other
                    # adjacent positions.
                    traverse_positions.append(adj_traverse)
                    if self._positions[adj_traverse] == player_num:
                        for pos in traverse_positions:
                            flip_pieces.append(pos)
                        break
                    adj_traverse += adj_diff

        # Now we actually flip the surrounded pieces
        for pos in flip_pieces:
            self._positions[pos] = player_num


    # [Board.show]
    # @description: Prints the board to stdout
    # @param1: Self
    # @param2: Human player (1 or 2), used to show available moves
    # @return: Nothing
    def show(self, available_moves=None):
        #board_chars = chr(0x0020)+unichr(0x25cb)+unichr(0x25cf)
        board_chars = u'\u0020\u25cb\u25cf'
        print("  a b c d e f g h")
        for i in range(64):
            if (i % 8) == 0:
                print str((i//8)+1),
            if i in available_moves:
                #print u'\u2a2f',
                print "x",
            else:
                #print board_chars[self._positions[i]],
                print self._positions[i],
            if (i % 8) == 7:
                print("")
