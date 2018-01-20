

class RandomGame(object):

    _board = Board()
    _player1_pieces = _board.get_player_pieces(1)
    _player2_pieces = _board.get_player_pieces(2)
    _player1_available_moves = _board.get_available_moves(1)
    _player2_available_moves = _board.get_available_moves(2)
    _game_state = ""

    # [RandomGame.start]
    # @description: Starts a random game, but does not play any moves.
    # @param1: Self
    def start(self):
        self._game_state = "player1_turn"

    # [RandomGame.play_next_move]
    # @description: Plays the next move
    # @return: The array position of the next move
    def play_next_move(self):

        self._player1_pieces = self._board.get_player_pieces(1)
        self._player2_pieces = self._board.get_player_pieces(2)

        move_pos = -1

        if self._game_state == "player1_turn":
            move_pos_index = randint(0, len(self._player1_available_moves)-1)
            move_pos = self._player1_available_moves[move_pos_index]
            move_row = (move_pos / 8) + 1
            move_col = (move_pos % 8) + 1
            self._board.play_move(1, move_row, move_col)
            self._player2_available_moves = self._board.get_available_moves(2)
            # Check if other player passes, or if game is over
            if len(self._player2_available_moves) == 0:
                self._player1_available_moves = self._board.get_available_moves(1)
                if len(self._player1_available_moves) == 0:
                    self._game_state = "game_over"
            else:
                self._game_state = "player2_turn"

        elif self._game_state == "player2_turn":
            move_pos_index = randint(0, len(self._player2_available_moves)-1)
            move_pos = self._player2_available_moves[move_pos_index]
            move_row = (move_pos / 8) + 1
            move_col = (move_pos % 8) + 1
            self._board.play_move(2, move_row, move_col)
            self._player1_available_moves = self._board.get_available_moves(1)
            # Check if other player passes, or if game is over
            if len(self._player1_available_moves) == 0:
                self._player2_available_moves = self._board.get_available_moves(2)
                if len(self._player2_available_moves) == 0:
                    self._game_state = "game_over"
            else:
                self._game_state = "player1_turn"

        return move_pos
