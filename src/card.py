class Card():
	def __init__(self, suit, value, face_or_ace):
		self.suit = suit
		self.value = value
		self.face_or_ace = face_or_ace

	def get_suit(self):
		return self.suit

	def get_value(self):
		return self.value

	def is_face_or_card(self):
		return self.face_or_ace