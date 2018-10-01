from __future__ import print_function
import sys
import time

class Player(object):
    '''
    The client through which players can play ERS through interacting and 
    polling the ERS game server. 
    '''

    def __init__(self):
        self.name = ""
        self.round = 1
    
    def initiate_game(self, game):
        '''
        Takes: itself, the game server object we'll be talking to 
        Returns: None, initiates the game
        '''
        # if a new player tries to join make sure the game server hasn't already started a game
        if game.get_locked_status(): print("The game has already started sorry you are unable to join at this time!")
        else:
            print("Hi there, welcome to the console based version of Egyptian Rat Screw :)")
            self.join_game(game)
            self.queue_for_game(game)

    def join_game(self, game):
        '''
        Takes: itself, the game server object we'll be talking to 
        Returns: None, allows players to join the game with a unique name
        '''
        while True:
            desired_name = input("Please enter your name: ").strip()

            # each name in the game needs to be unique otherwise there will be confusion
            if desired_name not in game.get_players():
                self.name = desired_name
                game.register_player(self.name)
                break
            else: print("That name is already taken ): Please try a different name")

    def queue_for_game(self, game):
        '''
        Takes: itself, the game server object we'll be talking to 
        Returns: None, queues a user to join the game essentially putting them in the game lobby
        '''
        self.game_print(("Hi {0}, thanks for joining the ERS game lobby! When there is more than one player and all players " + 
            "are in agreement to start the game, the game will start.").format(self.name))

        # allow a user to signal that they are ready, check the ready status of other players in the lobby, and quit the game
        while True:
            self.lobby_menu()
            response = input("Type a command: ").strip()
            if response == "s" or response == "start": 
                self.game_print("As soon as the other players in the lobby are ready we'll begin the game!!!")
                break
            elif response == "c" or response == "check": self.game_print(game.get_lobby_status())
            elif response == "q" or response == "quit": 
                game.quit_game(self.name)
                return
            else: self.game_print("Please enter a valid command!")
        self.wait_for_start(game)


    def wait_for_start(self, game):
        '''
        Takes: itself, the game server object we'll be talking to 
        Returns: None
        '''
        game.signal_ready(self.name)
        # wait for the game to start
        while True:
            if game.get_start_status(): 
                self.start_game(game)
                break

    def start_game(self, game):
        '''
        Takes: itself, the game server object we'll be talking to 
        Returns: None, starts the game officially for the player
        Raises: Exception if client somehow becomes out of sync with the server
        '''
        self.game_print("The game will start now, you can enter \"s\" or \"slap\" to slap or you can just press enter " +
                        "to continue without slapping")

        # the game will continue until a player has all the cards in the game
        while True:
            winner = game.get_winner()

            # check first if there is a winner from the previous round, if there is break and end the game
            if winner: 
                self.game_print("The winner of this game is " + winner + "!!!!!")
                break

            # get round number and status 
            current_round, current_card, current_flipper = game.get_round()
            self.game_print(("It is now round {0}. The card flipped this turn by {1} is {2}").format(current_round, current_flipper, current_card))
            self.game_print(("Keep in mind that you have {0} cards left in your hand!!").format(game.get_num_cards(self.name)))

            # allow users to slap, they can press anything other than the slap command to continue otherwise
            slap = input("Do you want to slap? Enter \"s\" or \"slap\" if so, press enter otherwise: ").strip()

            # if the user does slap, we need to send the system timestamp with millisecond resolution 
            # to deal with any possible network latency
            if slap == "s" or slap == "slap": game.slap_attempt(self.name, int(round(time.time() * 1000)))

            # every round a player can only decide whether to slap or not, after that they automatically signal ready
            game.signal_ready(self.name)

            # wait for round results
            while True:

                # the server started a new round
                if game.get_round_number() > self.round: 
                    if game.get_round_number() > self.round + 1: raise Exception("Client is out of sync with server")
                    self.round += 1
                    break

            # print the results of the round once all players have made a move for that specific round
            print(("------------------------------ ROUND {0} RESULTS --------------------------").format(self.round - 1))
            print(game.get_round_results())
            print(("------------------------------ ROUND {0} RESULTS --------------------------").format(self.round - 1))

        self.game_print("Thank you for playing terminal ERS :)")


    def lobby_menu(self):
        ''' ERS Game Lobby Menu of Possible Commands '''
        self.game_print("--------------------------- ERS LOBBY MENU ---------------------------")
        self.game_print("s or start: attempts to start the game | requires all players in the lobby to start the game")
        self.game_print("c or check: checks the status of players in the lobby")
        self.game_print("q or quit: quit the lobby entirely")
        self.game_print("----------------------------------------------------------------------")

    def game_print(self, text=""):
        ''' Game relevant print method '''
        print(("ERS [{0}]: " + text).format(self.name))
