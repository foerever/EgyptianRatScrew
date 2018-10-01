import sys
import Pyro4
import Pyro4.util
import sys

sys.path.insert(0, '/src/client.py')
from client import Player

sys.excepthook = Pyro4.util.excepthook

game = Pyro4.Proxy("PYRONAME:ERS")
player = Player()
player.initiate_game(game)
