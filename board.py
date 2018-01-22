import numpy as np

BLACK = 1
WHITE = 2

class Board(object):

    # _board = [
    #     0, 0, 0, 0, 0, 0, 0, 0,
    #     0, 0, 0, 0, 0, 0, 0, 0,
    #     0, 0, 0, 0, 0, 0, 0, 0,
    #     0, 0, 0, 2, 1, 0, 0, 0,
    #     0, 0, 0, 1, 2, 0, 0, 0,
    #     0, 0, 0, 0, 0, 0, 0, 0,
    #     0, 0, 0, 0, 0, 0, 0, 0,
    #     0, 0, 0, 0, 0, 0, 0, 0,
    # ]
    _board = np.zeros(64, np.int8)
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
    
    _player_pieces = [[],[],[]]
    _available_moves = [[],[],[]]

    # [Board.init]
    # @description Constructor
    def __init__(self):
        self._player_pieces[BLACK] = [28, 35]
        self._player_pieces[WHITE] = [27, 36]
        for p in self._player_pieces[BLACK]: self._board[p] = BLACK
        for p in self._player_pieces[WHITE]: self._board[p] = WHITE
        self.set_available_moves(BLACK)
        self.set_available_moves(WHITE)

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

    # [Board.set_player_pieces]
    # @param1: Self
    # @param2: Player to set pieces for (1 or 2)
    # @return: Nothing. Set list of pieces, then exit.
    def set_player_pieces(self, player_num):
        pieces = []
        for i in range(64):
            if self._board[i] == player_num:
                pieces.append(i)
        self._player_pieces[player_num] = pieces

    # [Board.set_available_moves]
    # @param1: Self
    # @param2: Player to set available moves for (1 or 2)
    # @return: Nothing. Set list of available moves, then exit.
    def set_available_moves(self, player_num):
        available_moves = []
        for pos in range(64):
            if self.is_legal_move(player_num, pos):
                available_moves.append(pos)
        self._available_moves[player_num] = available_moves

    # [Board.play_move]
    # @description: Play a move, flip all necessary pieces. Important, we 
    #   assume the move is legal!
    # @param1: Self
    # @param2: Player number to play move for (1 or 2)
    # @param3: Move position (0 to 63)
    def play_move(self, player_num, move_pos):

        # First, set the move position
        self._board[move_pos] = player_num

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
            if player_num + self._board[adj] == 3:
                # Traverse the board in the direction of the opponent piece.
                # Keep track of all the position indicies on our path.
                adj_diff =  adj - move_pos
                adj_traverse = move_pos + adj_diff
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
    # @param1: Self
    # @param2: Human player (1 or 2), used to show available moves
    # @return: Nothing
    def show(self, human_player):
        #board_chars = chr(0x25ef)+chr(0x25cb)+chr(0x25cf)
        board_chars = chr(0x0020)+chr(0x25cb)+chr(0x25cf)
        print("  a b c d e f g h")
        for i in range(64):
            if (i % 8) == 0:
                print(str((i//8)+1) + " ", end='')
            if i in self._available_moves[human_player]:
                print(str(chr(0x2a2f)) + " ", end='')
            else:
                print(str(board_chars[self._board[i]]) + " ", end='')
            if (i % 8) == 7:
                print("")
