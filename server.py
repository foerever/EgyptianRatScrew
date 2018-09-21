from __future__ import print_function
import Pyro4


@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Game(object):
    def __init__(self):
        self.contents = ["1", "2", "3"]
        self.players = []

    def begin_game(self, player):
        player.player_print("testing")
        # print("{0} has joined the game!".format(name))
        # self.players.append(name)


def main():
    Pyro4.Daemon.serveSimple(
            {
                Game: "ERS"
            },
            ns = True)

if __name__=="__main__":
    main()