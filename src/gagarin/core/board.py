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
        """
        Constructor.
        """
        super(Board, self).__init__(**properties)

    def create_memento(self):
        """
        Serialize board object.

        :rtype: str
        """
        return pickle.dumps(vars(self))

    def set_memento(self, memento):
        """
        Restore board object state from a string.

        You can create string representing board state with create_memento
        method of Board class.

        :param memento: string representing board state
        :type memento: str
        :return: current instance
        :rtype: Board
        """
        previous_state = pickle.loads(memento)
        vars(self).clear()
        vars(self).update(previous_state)
        return self

    def save_to_file(self, file):
        """
        Save board state to file.

        :param file: file object to save board state
        :type filename: file-like object
        :return: current instance
        :rtype: Board
        """
        file.write(self.create_memento())
        return self

    def load_from_file(self, file):
        """
        Load board state from file.

        :param filename: file object to load board state
        :type filename: file-like object
        :return: current instance
        :rtype: Board
        """
        return self.set_memento(file.read())
