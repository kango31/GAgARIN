#!encoding: utf-8

"""
Base class for a card in game.
"""
from .zone import Zone


class Card(Zone):
	"""
	Base class for a card in game.
	"""
	def __init__(self, **properties):
		"""
		Constructor.

		:param properties: properties of the card
		:type properties: dict
		"""
		super(Card, self).__init__(**properties)
		self._face_up = True
		self._angle = 0

	def is_face_up(self):
		"""
		State whether card is face up.

		:rtype: bool
		"""
		return self._face_up

	def is_face_down(self):
		"""
		State whether card is face down.

		:rtype: bool
		"""
		return not self._face_up

	def is_visible(self):
		"""
		State whether component is visible.

		:rtype: bool
		"""
		return self.is_face_up()

	def flip(self):
		"""
		Flip card.

		:return: current instance
		:rtype: Card
		"""
		self._face_up = not self._face_up
		return self

	def set_face_up(self, toggle=True):
		"""
		Set card face up.

		:param toggle: toggle for face up card
		:type toggle: bool
		:return: current instance
		:rtype: Card
		"""
		self._face_up = toggle
		return self

	def set_face_down(self, toggle=True):
		"""
		Set card face down.

		:param toggle: toggle for face down card
		:type toggle: bool
		:return: current instance
		:rtype: Card
		"""
		self._face_up = not toggle
		return self

	def rotate(self, value):
		"""
		Rotate card by the specified value angle.

		This angle is added to the current card rotation angle.

		:param value: rotation angle for card
		:type value: int
		:return: current instance
		:rtype: Card
		"""
		self._angle += int(value)
		return self

	def set_rotation(self, value):
		"""
		Set rotation angle of card to specified value.

		:param value: rotation angle for card
		:type value: int
		:return: current instance
		:rtype: Card		
		"""
		self._angle = int(value)
		return self

	def get_rotation(self):
		"""
		Get rotation angle of card.

		:return: rotation angle
		:rtype: int
		"""
		return self._angle

	def tap(self):
		"""
		Tap card, shortcut for setting rotation to 90°.

		:return: current instance
		:rtype: Card				
		"""
		self.set_rotation(90)
		return self

	def untap(self):
		"""
		Untap card, shortcut for setting rotation to 0°.

		:return: current instance
		:rtype: Card				
		"""		
		self.set_rotation(0)
		return self

	def is_tapped(self):
		"""
		State whether card is tapped.

		:return: is card tapped ?
		:rtype: bool
		"""
		return self._angle == 90

	def is_untapped(self):
		"""
		State whether card is untapped.

		:return: is card untapped ?
		:rtype: bool
		"""
		return self._angle == 0
