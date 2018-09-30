from __future__ import print_function
from collections import defaultdict
import Pyro4

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Game(object):
    def __init__(self):
        self.players = defaultdict(bool)
        self.locked = False
        self.started = False

    def get_locked_status(self):
        return self.locked

    def get_start_status(self):
        return self.started

    def get_players(self):
        return self.players.keys()

    @Pyro4.expose
    def register_player(self, name):
        if not self.locked: 
            print(("{0} joined the game").format(name))
            self.players[name] = False

    @Pyro4.expose
    def quit_game(self, name):
        self.players.pop(name, None)

    def get_lobby_status(self):
        s = "\n\nLobby Status: \n"
        for player in self.players.keys():
            if self.players[player]: s += player + " is ready \n"
            else: s += player + " is not ready \n"
        return s

    @Pyro4.expose
    def signal_start(self, name):
        self.players[name] = True
        if len(self.players.keys()) > 1: 
            all_ready = True
            for ready_status in self.players.values():
                if not ready_status: all_ready = False
            if all_ready: self.started, self.locked = True, True

def main():
    Pyro4.Daemon.serveSimple(
            {
                Game: "ERS"
            },
            ns = True)

if __name__== "__main__":
    main()