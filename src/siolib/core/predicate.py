"""
This module defines a class to interpret predicates from strings.
"""

import re
from .parser import DslLexer, DslParser


class PropertyError(KeyError):
    """
    Custom exception when trying to get a non-existing property from component.
    """
    def __init__(self, msg):
        """
        Constructor.

        :param msg: non-existing property
        :type msg: str
        """
        super(PropertyError, self).__init__(msg)


class Predicate():
    """
    Convert a query in a form of a string into a predicate to be used on a
    Component. If a function-like object is provided, then it is used as-is.
    """
    def __init__(self, query):
        """
        Constructor.

        :param query: query string or function object
        :type: str or callable
        """
        if not callable(query):
            self._query = query
            self._func = None
        else:
            self._func = query
            self._query = None
        self._lexer = DslLexer()
        self._parser = DslParser()

    def __call__(self, component):
        """
        Evaluate the query on given component.

        :param component: component to be checked
        :type component: Component
        :return: True if component passes the predicate and False otherwise
        :rtype: bool
        """
        if self._func is not None:
            try:
                return self._func(component)
            except PropertyError:
                return False
        else:
            try:
                self._parser.attach(component)
                tokens = self._lexer.tokenize(self._query)
                return self._parser.parse(tokens)
            except PropertyError:
                return False
