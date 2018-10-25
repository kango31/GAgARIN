#!encoding: utf-8

"""
Base class for board.
"""
import pickle


from .zone import Zone, Component


class Board(Zone):
	"""
	Abstraction of a full board with memento design pattern.
	"""
	def __init__(self, **properties):
		super(Board, self).__init__(**properties)

	def create_memento(self):
		return pickle.dumps(vars(self))

	def set_memento(self, memento):
		previous_state = pickle.loads(memento)
		vars(self).clear()
		vars(self).update(previous_state)
