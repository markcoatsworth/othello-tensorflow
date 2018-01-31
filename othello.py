#!/usr/bin/env python

from game import Game

import sys

BLACK = 1
WHITE = 2


def main():

    human_player = BLACK
    robot_battle = False

    # Read command line args. Assume this is a human vs. computer game, with
    # human playing first, unless told otherwise.
    for arg in sys.argv:
        if(arg == "--help"):
            print("Options:")
            print("--white: Human plays white, computer goes first")
            print("--robot-battle: Computer plays against itself")
        if(arg == "--white"):
            human_player = WHITE
        if(arg == "--robot-battle"):
            robot_battle = True
        

    game = Game()

    # Human vs computer
    if not robot_battle:
        game.play_human(human_player)

    # Computer vs computer
    else:
        game.robot_battle()


if __name__ == "__main__":
    main()
