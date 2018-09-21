from __future__ import print_function
import sys

if sys.version_info < (3, 0):
    input = raw_input


class Player(object):
    def __init__(self, game):
        self.game = game
        self.set_name()
        self.name = ""
    
    def set_name(self):
        self.name = input("Enter your name: ").strip()
        self.queue_for_game()

    def queue_for_game(self):
        print("Your name is {0}.".format(self.name))
        response = input("Press enter when you are ready to begin the game: ").strip()
        # if response:
        print("Welcome to the game")
        self.game.begin_game(self)

    def player_print(self, message):
        print(message)