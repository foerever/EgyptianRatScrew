from collections import deque
import random
from card import Card

class Deck():
	'''
	The python object for a deck of cards which in turn
	holds cards of class Card
	'''

	def __init__(self):
		self.suits = ["Diamonds", "Clubs", "Hearts", "Spades"]
		self.values = ["2", "3", "4", "5", "6", "7", "8", "9", "10"]
		self.specials = ["Jack", "Queen", "King", "Ace"]
		self.deck = deque()

	def size(self):
		''' Gets the current size of the deck '''
		return len(self.deck)

	def is_empty(self):
		''' Gets boolean True or False for if the deck is empty '''
		return False if self.deck else True

	def shuffle_deck(self):
		''' Shuffles the deck '''
		random.shuffle(self.deck)

	def generate_fresh_deck(self):
		'''
		Takes: itself
		Returns: None, generates a standard 52 card deck
		'''
		for suit in self.suits:
			for value in self.values:
				self.add(Card(suit, value, False))
			for special in self.specials:
				self.add(Card(suit, special, True))

	def add(self, card):
		'''
		Takes: itself, a card of type Card to be added to the deck
		Returns: None, adds input card to deck as long as it is of the class Card
		'''
		if type(card) is Card: self.deck.append(card)
		else: raise ValueError("You can only add objects of the class type Card to the deck")

	def will_be_empty(self, num):
		''' 
		Takes: itself, number of cards to theoretically be taken from the deck
		Returns: boolean True if num cards can't be taken from the deck, False otherwise
		'''
		return True if len(self.deck) - num < 0 else False


	def take_top(self):
		'''
		Takes: itself
		Returns: the top card from the deck
		Raises: ValueError if the deck is empty
		'''
		if self.deck: return self.deck.pop()
		else: raise ValueError("You can't take from an empty deck!!!")


