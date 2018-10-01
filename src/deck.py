from collections import deque
import random
from card import Card

class Deck():
	def __init__(self):
		self.suits = ["Diamonds", "Clubs", "Hearts", "Spades"]
		self.values = ["2", "3", "4", "5", "6", "7", "8", "9", "10"]
		self.specials = ["Jack", "Queen", "King", "Ace"]
		self.deck = deque()

	def generate_fresh_deck(self):
		for suit in self.suits:
			for value in self.values:
				if value not in ["3", "4", "5", "6", "7", "8", "9", "10"]:
					self.add(Card(suit, value, False))
			for special in self.specials:
				if special not in ["Queen", "King", "Ace"]:
					self.add(Card(suit, special, True))

	def add(self, card):
		if type(card) is Card: self.deck.append(card)
		else: raise ValueError("You can only add objects of the class type Card to the deck")

	def size(self):
		return len(self.deck)

	def is_empty(self):
		return False if self.deck else True

	def will_be_empty(self, num):
		return True if len(self.deck) - num < 0 else False


	def take_top(self):
		if self.deck: return self.deck.pop()
		else: raise ValueError("You can't take from an empty deck!!!")

	def shuffle_deck(self):
		random.shuffle(self.deck)


