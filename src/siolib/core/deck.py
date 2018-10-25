#!encoding: utf-8

"""
Base class for a deck in game. A deck is a collection of cards
"""
import random

from .zone import Component
from .card import Card


class Deck(Component):
	"""
	Deck class: collection of cards.
	"""
	def __init__(self, face_up=False, **properties):
		"""
		Constructor.

		:param face_up: by default, all cards in this deck are considered as specified
		:type face_up: bool
		"""
		super(Deck, self).__init__(**properties)
		self._face_up = face_up
		self._cards = [ ]

	def add(self, card, position="top"):
		"""
		Add a card to deck at specified position {top, bottom, random}

		:param card: card to be added
		:type card: Card
		:param position: position of card in deck
		:type position: str
		:return: current deck
		:rtype: Deck
		"""
		if position == "top":
			self._cards.insert(0, card.set_face_up(self._face_up))
		elif position == "bottom":
			self._cards.append(card.set_face_up(self._face_up))
		elif position == "random":
			index = random.randint(0, len(self))
			self._cards.insert(index, card.set_face_up(self._face_up))
		else:
			raise ValueError("Unknown 'position' for Deck.add: {}".format(position))
		return self

	def __len__(self):
		"""
		Return number of cards in deck.

		:return: number of cards
		:rtype: int
		"""
		return len(self._cards)

	def shuffle(self):
		"""
		Shuffle deck.

		:return: current deck
		:rtype: Deck
		"""
		random.shuffle(self._cards)
		return self

	def draw(self, number=1, face_up=True):
		"""
		Draw cards from the deck.

		:param number: number of cards to be drawn
		:type number: int
		:param face_up: indicate if card is drawn face up.
		:type face_up: bool
		:return: drawn cards
		:rtype: list
		"""
		out = [ ]
		for i in range(number):
			try:
				card = self._cards.pop(0)
			except IndexError:
				break
			else:
				out.append(card.set_face_up(face_up))
		return out

	def search(self, filter, number=0):
		"""
		Search and draw card from deck.

		The card are filtered by the given filter function which is a function taking card as argument.
		By default, all cards matching the filter are drawn and returned but it is possible to limit the
		number of cards with number argument.

		:param filter: filter function for cards
		:type filter: function
		:param number: maximum number of cards to be returned
		:type number: int
		"""
		out = [ ]
		i = 0
		while True:
			card = self._cards[i].set_face_up(True)
			if filter(card):
				out.append(self._cards.pop(i))
			else:
				i += 1
				card.set_face_down()
			if i >= len(self):
				break
			if number > 0 and len(out) >= number:
				break
		return out

	def deal(self, piles, cards_per_pile, face_up=True):
		"""
		Deal 'cards_per_pile' cards into specified number of piles.

		:param piles: number of piles
		:type piles: int
		:param cards_per_pile: number of cards in a single pile
		:type cards_per_pile: int
		:param face_up: indicate if cards are drawn face up.
		:type face_up: bool
		:return: piles
		:rtype: list of list
		"""
		out = [ ]
		for p in range(piles):
			out.append([])
		i = 0
		stop = False
		while not stop:
			card = self._cards.pop(0).set_face_up(face_up)
			out[i].append(card)
			i = (i + 1) % piles
			stop = True
			for p in out:
				if len(self) == 0:
					pass
				elif len(p) != cards_per_pile:
					stop = False
		return out
