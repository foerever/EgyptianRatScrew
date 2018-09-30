# This is the code that starts ERS.
import sys
import Pyro4
import Pyro4.util
from single_computer_tester import Tester

sys.excepthook = Pyro4.util.excepthook

game = Pyro4.Proxy("PYRONAME:ERS")
tester = Tester()
tester.initiate_game(game)
