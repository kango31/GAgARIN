#!encoding: utf-8

class Agent():
    def __init__(self, name):
        self._name = name

    def get_name(self):
        return self._name

    def reset(self):
        pass

    def take_actions(self, game, phase):
        raise NotImplementedError


class Action():
    def __init__(self, **properties):
        """
        Constructor.
        """
        for key, value in properties.items():
            setattr(self, key, value)
