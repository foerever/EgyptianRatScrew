import sys
import Pyro4
import Pyro4.util
import sys
from client import Player

# instantiates a client through which a user can join the ERS game
game = Pyro4.Proxy("PYRONAME:ERS")
player = Player()
player.initiate_game(game)
