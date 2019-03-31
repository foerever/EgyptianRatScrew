import sys
import Pyro4
import Pyro4.util
import sys
from client import Player

# instantiates a client through which a user can join the ERS game
nameserver=Pyro4.locateNS()
uri=nameserver.lookup("ERS")
game = Pyro4.Proxy(uri)
player = Player()
player.initiate_game(game)
