#!encoding: utf-8

import pickle
import tempfile
import os

import pytest

from siolib.core.board import Board
from siolib.core.zone import Zone
from siolib.core.deck import Deck
from siolib.core.card import Card
from siolib.core.token import Token


class MyCard(Card):
    def __init__(self, facevalue, colour):
        Card.__init__(self, facevalue=facevalue, colour=colour)
    def __unicode__(self):
        return u"{}{}".format(self.facevalue, self.colour)


@pytest.fixture(scope="module")
def standard_poker():
    deck = Deck(name="Deck")
    facevalues=["A", "K", "Q", "J", "10", "9", "8", "7", "6", "5", "4", "3", "2"]
    colours = [u"\u2660", u"\u2665", u"\u2666", u"\u2663"] #Spades, Hearts, Diamonds, Clubs
    for c in colours:
        for fv in facevalues:
            deck.add(MyCard(facevalue=fv, colour=c))
    deck.shuffle()
    yield deck


@pytest.fixture(scope="module")
def board(standard_poker):
    board = Board(name="Poker")
    central = Zone(name="Central")
    player1 = Zone(name="Player1")
    player2 = Zone(name="Player2")
    board.add(central)
    board.add(player1)
    board.add(player2)
    hand1 = Zone(name="Hand1")
    hand2 = Zone(name="Hand2")
    player1.add(hand1)
    player2.add(hand2)
    central.add(standard_poker)
    stack1 = Zone(name="Stack1")
    stack2 = Zone(name="Stack2")
    player1.add(stack1)
    player2.add(stack2)
    for v in [500, 500, 1000, 1000, 2000, 2000, 5000, 5000]:
        for s in [stack1, stack2]:
            s.add(Token(value=v))
    yield board


class TestBoard(object):
    def test_get(self, board):
        assert board.get("name") == "Poker"

    def test_memento(self, board):
        save = board.create_memento()
        deck = board.search_component(lambda x: x.get("name") == "Deck")
        assert deck is not None
        hand1 = board.search_component(lambda x: x.get("name") == "Hand1")
        assert hand1 is not None
        hand2 = board.search_component(lambda x: x.get("name") == "Hand2")
        assert hand2 is not None
        out = deck.deal(2, 2)
        for c in out[0]:
            hand1.add(c)
        for c in out[1]:
            hand2.add(c)
        assert len(deck) == 48
        class CountMatch(object):
            def __init__(self):
                self.count = 0
            def __call__(self, component):
                self.count += 1
            def reset(self):
                self.count = 0
                return self
        algo = CountMatch()
        hand1.apply(algo.reset(), lambda x: isinstance(x, Card))
        assert algo.count == 2
        hand2.apply(algo.reset(), lambda x: isinstance(x, Card))
        assert algo.count == 2
        board.set_memento(save)
        deck = board.search_component(lambda x: x.get("name") == "Deck")
        hand1 = board.search_component(lambda x: x.get("name") == "Hand1")
        hand2 = board.search_component(lambda x: x.get("name") == "Hand2")
        assert len(deck) == 52
        hand1.apply(algo.reset(), lambda x: isinstance(x, Card))
        assert algo.count == 0
        hand2.apply(algo.reset(), lambda x: isinstance(x, Card))
        assert algo.count == 0

    def test_save_and_load(self, board):
        stack1 = board.search_component(lambda x: x.get("name") == "Stack1")
        assert not stack1.is_leaf()
        token = stack1.search_component(lambda x: x.get("value") == 500)
        stack1.remove(token)
        sum = 0
        for token in stack1:
            sum += token.get("value")
        assert sum == 16500
        handle, tmpfile = tempfile.mkstemp()
        with open(tmpfile, "wb") as fobj:
            board.save_to_file(fobj)
        with open(tmpfile, "rb") as fobj:
            board2 = Board()
            board2.load_from_file(fobj)
        os.remove(tmpfile)
        assert board2.get("name") == "Poker"
        for name, total in [("Stack1", 16500), ("Stack2", 17000)]:
            stack = board2.search_component(lambda x: x.get("name") == name)
            sum = 0
            for token in stack:
                sum += token.get("value")
            assert sum == total
