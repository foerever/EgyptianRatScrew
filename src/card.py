class Card():
	'''
	The python object for a standard card which can have 
	suits, numbers, faces, and aces
	'''

	def __init__(self, suit, value, face_or_ace):
		self.suit = suit
		self.value = value
		self.face_or_ace = face_or_ace

	def get_suit(self):
		''' Gets the suit of the card '''
		return self.suit

	def get_value(self):
		''' Gets the value of the card '''
		return self.value

	def is_face_or_ace(self):
		''' Gets boolean True if the card is a face or ace, False otherwise '''
		return self.face_or_ace