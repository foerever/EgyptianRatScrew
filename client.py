from __future__ import print_function
import serpent
import sys
import time

if sys.version_info < (3, 0):
    input = raw_input


class Player(object):
    def __init__(self):
        self.name = ""
        self.round = 1
    
    def initiate_game(self, game):
        if game.get_locked_status(): print("The game has already started sorry you are unable to join at this time!")
        else:
            print("Hi there, welcome to Egyptian Rat Screw :)")
            self.join_game(game)
            self.queue_for_game(game)

    def join_game(self, game):
        while True:
            desired_name = input("Please enter your name: ").strip()
            # each name in the game needs to be unique otherwise there will be confusion
            if desired_name not in game.get_players():
                self.name = desired_name
                game.register_player(self.name)
                break
            else: print("That name is already taken ): Please try a different name")

    def queue_for_game(self, game):
        self.game_print(("Hi {0}, thanks for joining the ERS game lobby! When there is more than one player and all players " + 
            "are in agreement to start the game, the game will start.").format(self.name))
        while True:
            self.lobby_menu()
            response = input("Type a command: ").strip()
            if response == "s" or response == "start": break
            elif response == "c" or response == "check": self.game_print(game.get_lobby_status())
            elif response == "q" or response == "quit": 
                game.quit_game(self.name)
                return
            else: self.game_print("Please enter a valid command!")
        game.signal_ready(self.name)
        self.wait_for_start(game)



    def wait_for_start(self, game):
        self.game_print("As soon as the other players in the lobby are ready we'll begin the game!!!")
        # wait for the game to start
        while True:
            if game.get_start_status(): 
                self.start_game(game)
                break

    def start_game(self, game):
        self.game_print("--------------------------- GAME START ---------------------------")
        self.game_print("The game will start now, you can enter \"s\" or \"slap\" to slap or you can just press enter " +
                        "to continue without slapping")
        while True:
            # get round number and status 
            current_round, current_card = game.get_round()
            self.game_print(("It is now round {0}. The card is {1}").format(current_round, current_card))
            slap = input("Do you want to slap? Enter \"s\" or \"slap\" if so: ").strip()
            if slap == "s" or slap == "slap": game.slap_attempt(self.name, int(round(time.time() * 1000)))
            game.signal_ready(self.name)

            # wait for round results
            while True:

                # the server started a new round
                if game.get_round_number() > self.round: 
                    if game.get_round_number() > self.round + 1: raise Exception("Client is out of sync with server")
                    self.round += 1
                    break

            print("------------------------------ GETTING ROUND RESULTS --------------------------")
            self.game_print(game.get_round_results())

    def lobby_menu(self):
        self.game_print("--------------------------- ERS LOBBY MENU ---------------------------")
        self.game_print("s or start: attempts to start the game | requires all players in the lobby to start the game")
        self.game_print("c or check: checks the status of players in the lobby")
        self.game_print("q or quit: quit the lobby entirely")
        self.game_print("----------------------------------------------------------------------")

    def game_print(self, text=""):
        print(("ERS [{0}]: " + text).format(self.name))
