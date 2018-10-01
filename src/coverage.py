import unittest
from client import Player
from server import GameServer
from deck import Deck
from card import Card
from collections import deque

class Test(unittest.TestCase):

	def test_game_server(self):
		game = GameServer()
		game.players["anthony"]["pile"]
		self.assertTrue(type(game.players["anthony"]["pile"]) is deque)

	def test_client(self):
		player = Player()
		player.round += 1
		actual = player.round
		expected = 2
		self.assertEqual(actual, expected)

	def test_card(self):
		card = Card("Diamonds", "3", True)
		self.assertTrue(card.is_face_or_ace())

	def test_deck(self):
		deck = Deck()
		deck.generate_fresh_deck()
		self.assertTrue(deck.size() == 52)

unittest.main(verbosity=2)