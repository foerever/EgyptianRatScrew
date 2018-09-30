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
        self.total_cards = self.deck.size()
        self.pile = deque()
        self.round = 0
        self.round_history = []
        self.round_result = ""
        self.current_card = ""
        self.winner = ""
        self.player_list = []
        self.slaps = []
        self.current_flipper = ""

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

    def get_round(self):
        return self.round, self.current_card, self.current_flipper

    def slap_attempt(self, name, timestamp):
        self.slaps.append((name, timestamp))

    def get_num_cards(self, name):
        return len(self.players[name]["pile"])

    def player_still_playing(self, name):
        return False if not self.players[name] else True

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
        if len(self.players.keys()) > 1 and self.players_ready(): 
            if not self.started: 
                self.started, self.locked = True, True
                self.distribute_cards() 
                self.player_list = list(self.players.keys())
            self.next_round()

    def distribute_cards(self):
        num_players = len(self.players.keys())
        while not self.deck.will_be_empty(num_players):
            for player in self.players.keys():
                self.players[player]["pile"].append(self.deck.take_top())

    def next_round(self):
        if self.players_ready():
            if self.round == 0: self.new_round()
            else:
                self.apply_round_results()
                self.new_round()

    def new_round(self):
        self.reset_players_status()
        self.slaps = []
        self.round += 1
        turn = self.round % len(self.player_list)

        # since the official game rules state players without anymore cards can still play, remaining players
        # must then accomodate by flipping their cards instead
        if self.players[self.player_list[turn]]["pile"]: card = self.players[self.player_list[turn]]["pile"].pop()
        else:
            next_person = self.round
            while True:
                next_person += 1
                turn = next_person % len(self.player_list)
                if self.players[self.player_list[turn]]["pile"]: 
                    card = self.players[self.player_list[turn]]["pile"].pop()
                    break

        self.round_history.append((self.player_list[turn], card))
        self.current_card = str(card.get_value()) + " of " + str(card.get_suit())
        self.current_flipper = self.player_list[turn]
        self.pile.append(card)

    def is_valid_slap(self):
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
        cards = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace"]
        top_card = self.round_history[self.round - 1][1].get_value()
        second_card = self.round_history[self.round - 2][1].get_value()
        third_card = self.round_history[self.round - 3][1].get_value()
        fourth_card = self.round_history[self.round - 4][1].get_value()
        card_list = [fourth_card, third_card, second_card, top_card]
        ascending = True
        descending = True
        for i in range(3):
            if cards.index(card_list[i]) + 1 != cards.index(card_list[i+1]): ascending = False
            if cards.index(card_list[i]) != cards.index(card_list[i+1]) - 1: descending = False
        return ascending or descending

    def apply_round_results(self):
        winner = ""
        winning_reason = ""
        losers = []
        result = "\n\n"
        if self.slaps and self.is_valid_slap(): 
            winner = min(self.slaps, key=lambda x:x[1])[0]
            winning_reason = " for slapping first and correctly!!!"
        elif self.round > 1 and (self.round_history[self.round - 2][1].is_face_or_card() 
            and not self.round_history[self.round - 1][1].is_face_or_card()): 
            winner = self.round_history[self.round - 2][0]
            winning_reason = " for being the last to put down a face or ace!!!"
        else:
            # punish everyone who slapped incorrectly
            for slap in self.slaps:
                losers.append(slap[0])
                if self.players[slap[0]]["pile"]: self.pile.appendleft(self.players[slap[0]]["pile"].pop())
                if self.players[slap[0]]["pile"]: self.pile.appendleft(self.players[slap[0]]["pile"].pop())
        if winner:
            self.players[winner]["pile"].extend(self.pile)
            random.shuffle(self.players[winner]["pile"])
            self.pile = deque()
            result += "The winner of this round is " + winner + winning_reason + "\n"
        else:
            for loser in losers:
                result += loser + " slapped incorrectly and lost 2 cards or whatever was remaining\n"
        self.round_result = result
        self.check_winner()

    def check_winner(self):
        for player in self.players.keys():
            if len(self.players[player]["pile"]) == self.total_cards: 
                self.winner = player

def main():
    Pyro4.Daemon.serveSimple(
            {
                Game: "ERS"
            },
            ns = True)

if __name__== "__main__":
    main()