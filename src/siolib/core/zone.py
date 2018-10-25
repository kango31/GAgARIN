#!encoding: utf-8

"""
Base class for zone and components
"""

class Component(object):
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
		If component is not visible, properties cannot be accessed.

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
			return cast(self._properties[name])
		else:
			return None

	# def __getattr__(self, name):
	# 	"""
	# 	Access the properties of the card as if they were attributes.

	# 	If component is not visible, this method returns None.

	# 	This method is only called if no attribute with given name has been found in self.__dict__.
	# 	The first check is made with __getattribute__ special method.

	# 	:param name: property name to be retrieved
	# 	:type name: str
	# 	:rtype: object		
	# 	"""
	# 	if not self.is_visible():
	# 		return None
	# 	else:
	# 		try:
	# 			return self.__dict__["_properties"][name]
	# 		except KeyError:
	# 			raise AttributeError("Object has no {} property.")

	# def __setattr__(self, name, value):
	# 	"""
	# 	Prevent the modification of component properties.

	# 	:param name: name of attribute to be modified
	# 	:type name: str
	# 	:param value: value of attribute
	# 	:type value: Python object
	# 	"""
	# 	if name in self._properties:
	# 		raise AttributeError("You cannot set the value of '{}'".format(name))
	# 	else:
	# 		super(Component, self).__setattr__(name, value)

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
		self._children = set()

	def add(self, component):
		"""
		Add a component to zone.

		:param component: component to be added
		:type component: Component
		:return: current zone
		:rtype: Zone
		"""
		self._children.add(component)
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
		except KeyError:
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

		:param predicate: predicate function taking a single argument
		:type predicate: function
		:return: matching component
		:rtype: Component
		"""
		#Find if it's a self match
		try:
			if predicate(self):
				return self
		except:
			pass
		#Then ask to children to find
		for c in self._children:
			if not c.is_leaf():
				result = c.search_component(predicate)
				if result is not None:
					return result
			else:
				try:
					if predicate(c):
						return c
				except:
					pass
		#Nothing has been found
		return None

	def apply(self, transform, predicate=None):
		"""
		Apply a transform function to all component matching the specified predicate.
		If no predicate is provided, the transformation is applied to all components.

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
		#Transform self
		try:
			if predicate(self):
				transform(self)
		except:
			pass
		#Transform children
		for c in self._children:
			if not c.is_leaf():
				c.apply(transform, predicate)
			else:
				try:
					if predicate(c):
						transform(c)
				except:
					pass
		#Return
		return self
