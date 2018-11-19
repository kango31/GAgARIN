#!encoding: utf-8

"""
Base classes for tokens in game.
"""
from .zone import Component
from .die import Face


class Token(Component):
	"""
	Suitable class for:

	- gems
	- cubes
	- coins
	- double-sided tokens with the same properties on both faces
	- meeples
	"""
	def __init__(self, **properties):
		"""
		Constructor.

		:param properties: properties of the token
		:type properties: dict
		"""
		super(Token, self).__init__(**properties)


class OneSidedToken(Token):
	"""
	Suitable for tokens with two faces (one generic and another one is specific).
	The generic side is used to identify the nature of token while specific side has an actual value hidden from player
	until revealed.
	"""
	def __init__(self, **properties):
		"""
		Constructor.

		The token is set to face down when created.

		:param properties: properties of the token
		:type properties: dict
		"""		
		super(OneSidedToken, self).__init__(**properties)
		self._face_up = False

	def is_visible(self):
		"""
		State whether component is visible.

		:rtype: bool
		"""
		return self._face_up

	def set_face_up(self, toggle):
		"""
		Set token face up.

		:param toggle: toggle for face up card
		:type toggle: bool
		:return: current instance
		:rtype: OneSidedToken
		"""
		self._face_up = toggle
		return self

	def set_face_down(self, toggle):
		"""
		Set token face up.

		:param toggle: toggle for face up card
		:type toggle: bool
		:return: current instance
		:rtype: OneSidedToken
		"""
		self._face_up = not toggle
		return self

	def flip(self):
		"""
		Flip token.

		:return: current instance
		:rtype: OneSidedToken
		"""
		self._face_up = not self._face_up
		return self

	def is_face_up(self):
		"""
		State whether token is face up.

		:rtype: bool
		"""
		return self._face_up


class TwoSidedToken(Token):
	"""
	Suitable for tokens with two specific faces.
	"""
	def __init__(self, face1, face2, **properties):
		"""
		Constructor.

		The face1 is by default faced up.

		:param face1: first face
		:type face1: Face
		:param face2: second face
		:type face2: Face		
		:param properties: properties of the token
		:type properties: dict
		"""		
		super(TwoSidedToken, self).__init__(**properties)
		self._visible_face = face1
		self._face1 = face1
		self._face2 = face2

	def flip(self):
		"""
		Flip token on the other side.

		:return: current token
		:rtype: TwoSidedToken
		"""
		if self._visible_face == self._face1:
			self._visible_face = self._face2
		else:
			self._visible_face = self._face1
		return self

	def set_visible_face(self, predicate):
		"""
		Set the visible face to any face matching the predicate.

		:param predicate: function taking a single argument
		:type predicate: function
		"""
		if predicate(self._face1):
			self._visible_face = self._face1
		elif predicate(self._face2):
			self._visible_face = self._face2
		return self

	def get_visible_face(self):
		"""
		Get the die visible face.

		:rtype: Face
		"""
		return self._visible_face