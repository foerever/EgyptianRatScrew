from __future__ import print_function
from collections import defaultdict
from collections import deque
import Pyro4
from deck import Deck
import random
import time

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class GameServer(object):
    '''  
    The ERS game server holds the state of a single game at a time. 
    Clients (players) can interact with the server but the server can 
    not interact with the clients. 
    '''

    def __init__(self):
        '''
        Initializes the primary Egyptian Rat Screw objects which 
        hold the state of the game.
        '''
        self.players = defaultdict(lambda:defaultdict(deque))
        self.locked = False
        self.started = False
        self.deck = Deck()
        self.deck.generate_fresh_deck()
        self.deck.shuffle_deck()
        self.total_cards = self.deck.size()
        self.pile = deque()
        self.round = 0
        self.round_history = []
        self.player_list = []
        self.slaps = []
        self.round_result = ""
        self.current_card = ""
        self.winner = ""
        self.current_flipper = ""

    def get_locked_status(self):
        ''' Gets the status of the server and whether it is locked from additional players '''
        return self.locked

    def get_start_status(self):
        ''' Gets the start status of the game '''
        return self.started

    def get_players(self):
        ''' Gets the current players registered with the game server '''
        return self.players.keys()

    def get_round_number(self):
        ''' Gets the current round of the game '''
        return self.round

    def get_round_results(self):
        ''' Gets the results from the last round '''
        return self.round_result

    def get_winner(self):
        ''' Gets the winner of the game, if there is not one it returns an empty string '''
        return self.winner

    def get_round(self):
        ''' Gets the round number, the card flipped in that round, and the player who flipped it '''
        return self.round, self.current_card, self.current_flipper

    def reset_players_status(self):
        ''' Reset ready status of all players to not ready '''
        for player in self.players.keys():
            self.players[player]["ready"] = False   

    def slap_attempt(self, name, timestamp):
        ''' 
        Takes: itself, the name of the player making the slap attempt, the time stamp of said slap attempt
        Returns: None, adds the slap attempt details to list of slap attempts for the current round
        '''
        self.slaps.append((name, timestamp))

    def get_num_cards(self, name):
        ''' 
        Takes: itself, the name of a player in the game 
        Returns: the number of cards the input player currently has 
        '''
        return len(self.players[name]["pile"])

    @Pyro4.expose
    def register_player(self, name):
        ''' 
        Takes: itself, name of player to register in the game
        Returns: None, registers a player for the game 
        '''
        if not self.locked: self.players[name]["ready"] = False

    @Pyro4.expose
    def quit_game(self, name):
        ''' 
        Takes: itself, name of player to be removed from the game
        Returns: None, removes input player from game state
        '''
        self.players.pop(name, None)

    def get_lobby_status(self):
        '''
        Takes: itself 
        Returns: ready status of players in the game lobby 
        '''
        s = "\n\nLobby Status: \n"

        # construct a string of those in the game lobby and their ready status
        for player in self.players.keys():
            if self.players[player]["ready"]: s += player + " is ready \n"
            else: s += player + " is not ready \n"
        return s

    def players_ready(self):
        '''
        Takes: itself
        Returns: boolean True if all players in the game are ready, False otherwise
        '''
        all_ready = True
        for player in self.players.keys():
            if not self.players[player]["ready"]: all_ready = False        
        return True if all_ready else False  

          

    @Pyro4.expose
    def signal_ready(self, name):
        ''' 
        Takes: itself and the unique name of the player who is signaling readiness
        Returns: None, signals that a player is ready for the game state
        '''
        self.players[name]["ready"] = True

        # if everyone in the game agrees to move on to the next round and there are 
        # enough people to play go ahead and move to the next round
        if len(self.players.keys()) > 1 and self.players_ready(): 

            # if we haven't started the game yet we need to lock it, mark it as started,
            # distribute the deck amongst the players, and get a copy of those playing
            if not self.started: 
                self.started, self.locked = True, True
                self.distribute_cards() 
                self.player_list = list(self.players.keys())
            self.next_round()

    def distribute_cards(self):
        '''
        Takes: itself
        Returns: None, distributes the deck of cards among the players in the game state 
        '''
        num_players = len(self.players.keys())

        # distribute cards n at a time where n is the number of players and where |deck| - n > -1
        while not self.deck.will_be_empty(num_players):
            for player in self.players.keys():
                self.players[player]["pile"].append(self.deck.take_top())

    def next_round(self):
        '''
        Takes: itself
        Returns: None, move on to the next round 
        '''
        if self.players_ready():
            # if we are just starting the round, we can move directly to it 
            if self.round == 0: self.new_round()
            else:
                # if all players are ready for a new round, we go ahead and employ their decisions by order of 
                # timestamp and move the game state to the next round 
                self.apply_round_results()
                self.new_round()

    def new_round(self):
        '''
        Takes: itself
        Returns: None, moves the game state to a new round
        '''
        self.reset_players_status()
        self.slaps = []
        self.round += 1
        turn = self.round % len(self.player_list)

        # Since the official game rules state players without anymore cards can still play, remaining players
        # must then accomodate by flipping their cards instead
        if self.players[self.player_list[turn]]["pile"]: card = self.players[self.player_list[turn]]["pile"].pop()
        else:
            next_person = self.round
            while True:
                next_person += 1
                turn = next_person % len(self.player_list)

                # the first player to have a pile will need to flip
                if self.players[self.player_list[turn]]["pile"]: 
                    card = self.players[self.player_list[turn]]["pile"].pop()
                    break

        # add to the pile, round histroy, and basic markers of the current round
        self.round_history.append((self.player_list[turn], card))
        self.current_card = str(card.get_value()) + " of " + str(card.get_suit())
        self.current_flipper = self.player_list[turn]
        self.pile.append(card)

    def is_valid_slap(self):
        '''
        Takes: itself
        Returns: boolean True or False of whether a slap in this round is valid
        '''
        r = self.round
        if not self.pile: return False

        # check if it is a slap on doubles
        if r > 1 and self.round_history[r - 1][1].get_value() == self.round_history[r- 2][1].get_value(): return True

        # check if it is a slap on sandwich
        elif r > 2 and self.round_history[r - 1][1].get_value() == self.round_history[r - 3][1].get_value(): return True

        # check if it is a slap on top bottom
        elif r > 1 and self.round_history[0][1].get_value() == self.round_history[r - 1][1].get_value(): return True

        # check if it is a slap on ascending or descending
        elif r > 3 and self.is_ascending_or_descending(): return True

        # otherwise we have a false slap
        return False
        
    def is_ascending_or_descending(self):
        '''
        Takes: itself
        Returns: boolean True or False for whether the top 4 cards in the main pile are ascending or descending
        '''
        cards = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace"]

        # get the top 4 elements in the pile from the round history
        top_card = self.round_history[self.round - 1][1].get_value()
        second_card = self.round_history[self.round - 2][1].get_value()
        third_card = self.round_history[self.round - 3][1].get_value()
        fourth_card = self.round_history[self.round - 4][1].get_value()
        card_list = [fourth_card, third_card, second_card, top_card]
        ascending = True
        descending = True

        # now we simply iterate up the card list and see whether there is an increasing or decreasing pattern 
        for i in range(3):
            if cards.index(card_list[i]) + 1 != cards.index(card_list[i+1]): ascending = False
            if cards.index(card_list[i]) != cards.index(card_list[i+1]) - 1: descending = False
        return ascending or descending

    def apply_round_results(self):
        '''
        Takes: itself
        Returns: None, applies the decisions made by players to the current round 
        '''
        winner = ""
        winning_reason = ""
        losers = []
        result = "\n\n"

        # we first consider and prioritize whether there was a valid slap 
        if self.slaps and self.is_valid_slap(): 
            # if there is a valid slap, we get the player who slapped early to resolution of millisecond
            winner = min(self.slaps, key=lambda x:x[1])[0]
            winning_reason = " for slapping first and correctly!!!"

        # we also want to consider if someone has won the round by simply playing a face or ace card
        elif self.round > 1 and (self.round_history[self.round - 2][1].is_face_or_card() 
            and not self.round_history[self.round - 1][1].is_face_or_card()): 
            winner = self.round_history[self.round - 2][0]
            winning_reason = " for being the last to put down a face or ace!!!"

        # otherwise punish anyone that slapped since they slapped incorrectly
        else:
            for slap in self.slaps:
                losers.append(slap[0])
                # remove 0-2 cards from each player, as much as is possible
                if self.players[slap[0]]["pile"]: self.pile.appendleft(self.players[slap[0]]["pile"].pop())
                if self.players[slap[0]]["pile"]: self.pile.appendleft(self.players[slap[0]]["pile"].pop())

        # if there is a winner we give that winner all the cards in the main pile and shuffle the newly merged pile
        if winner:
            self.players[winner]["pile"].extend(self.pile)
            random.shuffle(self.players[winner]["pile"])
            self.pile = deque()
            result += "The winner of this round is " + winner + winning_reason + "\n"

        # otherwise we can see if there were any losers in that round who slapped incorrectly
        else:
            for loser in losers:
                result += loser + " slapped incorrectly and lost 2 cards or whatever was remaining\n"
        self.round_result = result

        # if there is a winner because of this round make note of it in the game state so when the client 
        # next polls the game can end with a winner
        self.check_winner()

    def check_winner(self):
        '''
        Takes: itself
        Returns: None, sets a winner in the game state if there exists a winner
        '''
        for player in self.players.keys():
            if len(self.players[player]["pile"]) == self.total_cards: 
                self.winner = player

def main():
    Pyro4.Daemon.serveSimple(
            {
                GameServer: "ERS"
            },
            ns = True)

if __name__== "__main__":
    main()