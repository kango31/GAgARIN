#!encoding: utf-8

from .predicate import Predicate, PropertyError

"""
Base class for zone and components
"""

class Component():
    """
    Base class for all components in game
    """
    def __init__(self, **properties):
        """
        Constructor.
        """
        super(Component, self).__setattr__("_properties", properties)

    def is_visible(self):
        """
        State wether the component is visible.
        If component is not visible, properties shall not be accessed.

        Derived class shall reimplement this method.

        :return: visibility of component
        :rtype: bool
        """
        return True

    def get(self, name, cast=None):
        """
        Access component property.

        A property cannot be accessed if component is not visible.
        An optional cast function taking a single argument may be provided to
        change the type of returned property.
        """
        if cast is None:
            cast = lambda x: x
        if self.is_visible():
            try:
                return cast(self._properties[name])
            except KeyError:
                raise PropertyError(name)
        else:
            return None

    def set(self, name, value):
        """
        Change value of specified property.
        """
        self._properties[name] = value

    def __getattr__(self, name):
        """
        Access the properties of the component as if they were attributes.

        If component is not visible, this method returns None.

        This method is only called if no attribute with given name has been
        found in self.__dict__. The first check is made with __getattribute__
        special method.

        :param name: property name to be retrieved
        :type name: str
        :rtype: object
        """
        try:
            return self.__dict__["_properties"][name]
        except KeyError:
            raise AttributeError("'{}' object has no property '{}'".format(
                    self.__class__.__name__, name))

    def __setattr__(self, name, value):
        """
        Set the value of component properties.

        :param name: name of property to be modified
        :type name: str
        :param value: value of property
        :type value: Python object
        """
        if "_properties" in self.__dict__ and name in self._properties:
            self._properties[name] = value
        else:
            super(Component, self).__setattr__(name, value)

    def is_leaf(self):
        """
        State whether this component is a leaf (it has no children).

        :rtype: bool
        """
        return True


class Zone(Component):
    """
    Base class for a zone in game.

    A zone is an aera of game where items may be put.
    It is implemented as a composite pattern to define various levels of zones.
    """
    def __init__(self, **properties):
        """
        Constructor.

        :param name: name of zone
        :type name: str
        """
        super(Zone, self).__init__(**properties)
        self._children = [ ]

    def add(self, component):
        """
        Add a component to zone.

        :param component: component to be added
        :type component: Component
        :return: current zone
        :rtype: Zone
        """
        self._children.append(component)
        return self

    def remove(self, component):
        """
        Remove a component from zone.

        :param component: component to be removed
        :type component: Component
        :return: current zone
        :rtype: Zone
        """
        try:
            self._children.remove(component)
        except ValueError:
            pass
        finally:
            return self

    def __len__(self):
        """
        Return number of components in zone.

        :return: number of components
        :rtype: int
        """
        return len(self._children)

    def is_leaf(self):
        """
        State whether this component is a leaf (it has no children).

        :rtype: bool
        """
        return False

    def search_component(self, predicate):
        """
        Find a component fulfilling given predicate.
        Recursively walk the tree to find a match.

        :param predicate: predicate function taking a single argument or string
        :type predicate: callable or str
        :return: matching component
        :rtype: Component
        """
        #Convert predicate if it's a string query
        predicate = Predicate(predicate)
        #Find if it's a self match
        if predicate(self):
            return self
        #Then ask to children to find
        for c in self._children:
            if not c.is_leaf():
                result = c.search_component(predicate)
                if result is not None:
                    return result
            else:
                if predicate(c):
                    return c
        #Nothing has been found
        return None

    def search_all_components(self, predicate=None):
        """
        Find all components fulfilling given predicate.
        Recursively walk the tree to find a match.

        :param predicate: predicate function taking a single argument or string
        :type predicate: callable or string
        :return: all matching components
        :rtype: list
        """
        output = []
        #Convert predicate if it's a string query
        if predicate is None:
            predicate = lambda x: True
        predicate = Predicate(predicate)
        #Find if it's a self match
        if predicate(self):
            output.append(self)
        #Then ask to children to find
        for c in self._children:
            if not c.is_leaf():
                result = c.search_all_components(predicate)
                output.extend(result)
            else:
                if predicate(c):
                    output.append(c)
        #Return all matches
        return output

    def apply(self, transform, predicate=None):
        """
        Apply a transform function to all component matching the specified predicate.
        If no predicate is provided, the transformation is applied to all components.

        The transformation function modifies the item inplace.

        :param transform: transformation function to be applied to matching components
        :type transform: function
        :param predicate: predicate function taking a single argument
        :type predicate: function
        :return: current zone
        :rtype: Zone
        """
        #Default predicate
        if predicate is None:
            predicate = lambda x: True
        #Convert predicate if it's a string query
        predicate = Predicate(predicate)
        #Transform self
        if predicate(self):
            transform(self)
        #Transform children
        for c in self._children:
            if not c.is_leaf():
                c.apply(transform, predicate)
            else:
                if predicate(c):
                    transform(c)
        #Return
        return self

    def __iter__(self):
        """
        Turn zone object into iterables.
        """
        return iter(self._children)

    def is_empty(self):
        """
        State whether zone is empty (it has no child).

        :rtype: bool
        """
        return len(self._children) == 0
