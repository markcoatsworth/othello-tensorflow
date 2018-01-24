import copy
import numpy as np

BLACK = 1
WHITE = 2

class Board(object):

    def __init__(self):
        self._positions = np.zeros(64, np.int8)
        self._weighted_positions = np.array([
            120, -20, 20,  5,   5,   20,  -20, 120,
            -20, -40, -5,  -5,  -5,  -5,  -40, -20,
            20,  -5,  15,  3,   3,   15,  -5,  20,
            5,   -5,  3,   3,   3,   3,   -5,  5,
            5,   -5,  3,   3,   3,   3,   -5,  5,
            20,  -5,  15,  3,   3,   15,  -5,  20,
            -20, -40, -5,  -5,  -5,  -5,  -40, -20,
            120, -20, 20,  5,   5,   20,  -20, 120
        ])

    # [Board.is_legal_move]
    # @param1: Self
    # @param2: Player number to play move for (1 or 2)
    # @param3: Board array positions to check (0 to 63)
    # @return: True if legal, False if not
    def is_legal_move(self, player_num, array_pos):
        
        if self._positions[array_pos] != 0:
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
            if player_num + self._positions[adj] == 3:
                # Traverse the board in the direction of the opponent piece
                # until we hit one of player_num's pieces (valid move) or we
                # hit an empty space or go off the board (invalid move)
                adj_diff =  adj - array_pos
                adj_traverse = array_pos + adj_diff
                # Watch out for the fucking edge of the board!
                while adj_traverse >= 0 and adj_traverse <= 63:
                    if self._positions[adj_traverse] == 0:
                        break
                    elif self._positions[adj_traverse] == player_num:
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

        # First, set the move position
        self._positions[move_pos] = player_num

        # Now make a list of all adjacent positions
        adjacent_positions=[ 
            (move_pos-9),   (move_pos-8),   (move_pos-7),
            (move_pos-1),                   (move_pos+1),
            (move_pos+7),   (move_pos+8),   (move_pos+9)
        ]
        # Trim invalid board spaces
        adjacent_positions = [x for x in adjacent_positions if (x >= 0 and x <= 63)]
        if move_pos % 8 == 0:
            adjacent_positions = [x for x in adjacent_positions if (x % 8 != 7)]
        elif move_pos % 8 == 7:
            adjacent_positions = [x for x in adjacent_positions if (x % 8 != 0)]

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
                    # Watch out for the left and right edges of the board!
                    # Need to make sure right/left and diagonal moves cannot
                    # cross the edges of the board, but up/down moves can run
                    # along left-most and right-most columns.
                    # The logic below is a disgusting mess. Try to clean it up?
                    if (adj_diff == 1 or adj_diff == 9) and adj_traverse % 8 == 7 and self._positions[adj_traverse] != player_num:
                        break
                    elif (adj_diff == -1 or adj_diff == -9) and adj_traverse % 8 == 0 and self._positions[adj_traverse] != player_num:
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
    def show(self, available_moves):
        #board_chars = chr(0x25ef)+chr(0x25cb)+chr(0x25cf)
        board_chars = chr(0x0020)+chr(0x25cb)+chr(0x25cf)
        print("  a b c d e f g h")
        for i in range(64):
            if (i % 8) == 0:
                print(str((i//8)+1) + " ", end='')
            if i in available_moves:
                print(str(chr(0x2a2f)) + " ", end='')
            else:
                print(str(board_chars[self._positions[i]]) + " ", end='')
            if (i % 8) == 7:
                print("")
