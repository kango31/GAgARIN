#!encoding: utf-8

"""
Base classes for dice in game.
"""
import random

from .zone import Component


class Face(Component):
	"""
	Abstraction for a token or die face.
	"""
	def __init__(self, **properties):
		"""
		Constructor.

		:param properties: properties of the die/token face
		:type properties: dict
		"""
		super(Face, self).__init__(**properties)


class Die(Component):
	"""
	Suitable class for all kind of dice.
	"""
	def __init__(self, faces, **properties):
		"""
		Constructor.

		:param faces: definition of faces
		:type faces: list of Component
		:param properties: properties of the die/token face
		:type properties: dict		
		"""
		super(Die, self).__init__(**properties)
		self._faces = faces
		self._visible_face = self._faces[0]

	def number_of_sides(self):
		"""
		Get the number of sides.

		:return: number of sides
		:rtype: int
		"""
		return len(self._faces)

	def roll(self):
		"""
		Roll the die: randomly change its visible face and return it.

		:rtype: Face
		"""
		self._visible_face = random.choice(self._faces)
		return self._visible_face

	def get_visible_face(self):
		"""
		Get the die visible face.

		:rtype: Face
		"""
		return self._visible_face

	def set_visible_face(self, predicate):
		"""
		Set the visible face to any face matching the predicate.

		:param predicate: function taking a single argument
		:type predicate: function
		"""
		for f in self._faces:
			if predicate(f):
				self._visible_face = f
				break
		return self
