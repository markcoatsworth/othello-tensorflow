#!/usr/bin/env python3.6

from game import Game

BLACK = 1
WHITE = 2


def main():

    # Human vs computer
    game = Game()
    game.play(BLACK) # Human goes first
    #game.play(WHITE) # Computer goes first

if __name__ == "__main__":
    main()
