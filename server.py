from __future__ import print_function
from collections import defaultdict
from collections import deque
import Pyro4
from deck import Deck
import random
import time

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Game(object):
    def __init__(self):
        self.players = defaultdict(lambda:defaultdict(deque))
        self.locked = False
        self.started = False
        self.deck = Deck()
        self.deck.generate_fresh_deck()
        self.deck.shuffle_deck()
        self.pile = deque()
        self.round = 0
        self.round_history = []
        self.round_result = ""
        self.current_card = ""
        self.winner = ""
        self.player_list = []
        self.slaps = []

    def get_locked_status(self):
        return self.locked

    def get_start_status(self):
        return self.started

    def get_players(self):
        return self.players.keys()

    def get_round_number(self):
        return self.round

    def get_round_results(self):
        return self.round_result

    def get_winner(self):
        return self.winner

    @Pyro4.expose
    def register_player(self, name):
        if not self.locked: 
            print(("{0} joined the game").format(name))
            self.players[name]["ready"] = False

    @Pyro4.expose
    def quit_game(self, name):
        self.players.pop(name, None)

    def get_lobby_status(self):
        s = "\n\nLobby Status: \n"
        for player in self.players.keys():
            if self.players[player]["ready"]: s += player + " is ready \n"
            else: s += player + " is not ready \n"
        return s

    def players_ready(self):
        all_ready = True
        for player in self.players.keys():
            if not self.players[player]["ready"]: all_ready = False        
        return True if all_ready else False  

    def reset_players_status(self):
        for player in self.players.keys():
            self.players[player]["ready"] = False             

    @Pyro4.expose
    def signal_ready(self, name):
        self.players[name]["ready"] = True
        if not self.started and len(self.players.keys()) > 1 and self.players_ready(): 
            self.instantiate_game()

    def instantiate_game(self):
        self.started, self.locked = True, True
        self.distribute_cards() 
        self.player_list = list(self.players.keys())
        self.new_round()
        self.start_game()

    def distribute_cards(self):
        num_players = len(self.players.keys())
        while not self.deck.will_be_empty(num_players):
            for player in self.players.keys():
                self.players[player]["pile"].append(self.deck.take_top())

    def new_round(self):
        self.reset_players_status()
        self.round += 1
        turn = self.round % len(self.player_list)
        card = self.players[self.player_list[turn]]["pile"].pop()
        self.round_history.append((self.player_list[turn], card))
        self.current_card = str(card.get_value()) + " of " + str(card.get_suit())

    def get_round(self):
        return self.round, self.current_card

    def slap_attempt(self, name, timestamp):
        self.slaps.append((name, timestamp))

    def is_valid_slap(self):
        top_card = self.round_history[self.round - 1][1]
        second_card = self.round_history[self.round - 2][1]
        third_card = self.round_history[self.round - 3][1]
        fourth_card = self.round_history[self.round - 4][1]
        if not self.pile: return False

        # check if it is a slap on doubles
        if top_card.get_value() == second_card.get_value(): return True

        # check if it is a slap on sandwich
        elif top_card.get_value() == third_card.get_value(): return True

        # check if it is a slap on ascending or descending
        elif self.is_ascending_descending([fourth_card, third_card, second_card, top_card]): return True

        # check if it is a slap on top bottom
        elif self.round_history[0][1] == top_card.get_value(): return True

        # otherwise we have a false slap
        return False
        
    def is_ascending_descending(self, card_list):
        cards = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace"]

        # check if we are ascending or descending
        if ((cards.index(card_list[0]) + 1 == cards.index(card_list[1]) 
            and cards.index(card_list[1]) + 1 == cards.index(card_list[2])
            and cards.index(card_list[2]) + 1 == cards.index(card_list[3])
            and cards.index(card_list[3]) + 1 == cards.index(card_list[4]))
            or 
            (cards.index(card_list[0]) - 1 == cards.index(card_list[1]) 
            and cards.index(card_list[1]) - 1 == cards.index(card_list[2])
            and cards.index(card_list[2]) - 1 == cards.index(card_list[3])
            and cards.index(card_list[3]) - 1 == cards.index(card_list[4]))):
            return True
        else: return False

    def apply_round_results(self):
        winner = ""
        losers = []
        result = "\n\n ROUND RESULTS: "
        # award the first correct slapper
        if self.is_valid_slap(): winner = min(self.slaps, key=lambda x:x[1])[0]
        elif (self.round_history[self.round - 2][1].is_face_or_card() 
            and not self.round_history[self.round - 1][1].is_face_or_card()): 
            winner = self.round_history[self.round - 2][0]
        else: 
            # punish everyone who slapped incorrectly
            for slap in self.slaps:
                losers.append(slap[0])
                self.pile.appendleft(self.players[slap[0]]["pile"].pop())
                self.pile.appendleft(self.players[slap[0]]["pile"].pop())
        if winner:
            self.players[winner]["pile"].extend(self.pile)
            random.shuffle(self.players[winner]["pile"])
            self.pile = deque()
            result += "The winner of this round is " + winner + " \n"
        else:
            for loser in losers:
                result += loser + " slapped incorrectly and lost 2 cards \n"
        self.round_result = result

    def winner_exists(self):
        for player in players.keys():
            if len(players[player]["pile"]) == 52:
                return player
        return ""


    def start_game(self):
        while True:
            if self.winner_exists(): 
                self.winner = self.winner_exists()
                break

            if self.players_ready():
                self.apply_round_results()
                self.new_round()

    def single_computer_start(self, name):
        self.players[name]["ready"] = True
        if len(self.players.keys()) > 1 and self.players_ready(): 
            self.players.pop(name, None)
            self.instantiate_game()

def main():
    Pyro4.Daemon.serveSimple(
            {
                Game: "ERS"
            },
            ns = True)

if __name__== "__main__":
    main()