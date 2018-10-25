"""
This module defines a class to interpret predicates from strings.
"""

import re


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

    def _build_dict(self, component):
        """
        Build a dictionnary for eval function based on query and given
        component.

        :param component: component to be passed to predicate
        :type component: Component
        :return: a dictionnary for the eval function
        :rtype: dict
        """
        #Get all variables from string
        #A variable is a regular Python variable name
        #If such a name is within quotes (single or double) it is ignored
        pattern = re.compile(r"""(?<!['"])\b\w+\b(?!['"])""")
        variables = pattern.findall(self._query)
        #Create dictionnary
        dct = {}
        for varb in variables:
            try:
                dct[varb] = component.get(varb)
            except KeyError:
                pass
        return dct

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
                return eval(self._query, self._build_dict(component))
            except PropertyError:
                return False
