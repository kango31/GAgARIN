import pytest

from gagarin.core.deck import Deck, Card
from gagarin.core.zone import Zone


#@pytest.fixture(scope="module")
@pytest.fixture
def empty_deck():
    yield Deck()

#@pytest.fixture(scope="module")
@pytest.fixture
def standard_poker():
    deck = Deck()
    facevalues=["A", "K", "Q", "J", "10", "9", "8", "7", "6", "5", "4", "3", "2"]
    colours = [u"\u2660", u"\u2665", u"\u2666", u"\u2663"] #Spades, Hearts, Diamonds, Clubs
    class MyCard(Card):
        def __init__(self, facevalue, colour):
            Card.__init__(self, facevalue=facevalue, colour=colour)
        def __unicode__(self):
            return u"{}{}".format(self.facevalue, self.colour)
    for c in colours:
        for fv in facevalues:
            deck.add(MyCard(facevalue=fv, colour=c))
    deck.shuffle()
    yield deck


class TestDeck(object):
    def test_add(self, empty_deck):
        assert empty_deck.is_empty()
        empty_deck.add(Card(facevalue="Ace", colour="Spades"), position="random")
        assert len(empty_deck) == 1
        empty_deck.add(Card(facevalue="Ace", colour="Hearts"), position="top")
        assert len(empty_deck) == 2
        empty_deck.add(Card(facevalue="Ace", colour="Clubs"), position="bottom")
        assert len(empty_deck) == 3
        empty_deck.add(Card(facevalue="Ace", colour="Diamonds"))
        assert len(empty_deck) == 4
        for card in empty_deck:
            assert card.facevalue == "Ace"

    def test_len(self, standard_poker):
        assert len(standard_poker) == 52

    def test_draw(self, standard_poker):
        cards = standard_poker.draw()
        assert len(cards) == 1
        assert len(standard_poker) == 51

    def test_draw_many(self, standard_poker):
        cards = standard_poker.draw(number=5)
        assert len(cards) == 5
        assert len(standard_poker) == 52 - 5
        cards = standard_poker.draw_all()
        assert standard_poker.is_empty()
        assert len(cards) == 52 - 5

    def test_draw_too_many(self, standard_poker):
        cards = standard_poker.draw(number=60)
        assert len(cards) == 52
        assert len(standard_poker) == 0

    def test_search(self, standard_poker):
        cards = standard_poker.search(lambda x: x.get("facevalue") == "A")
        assert len(cards) == 4
        for c in cards:
            assert c.get("facevalue") == "A"
        cards = standard_poker.search(lambda x: x.get("colour") == u"\u2665")
        assert len(cards) == 12
        for c in cards:
            assert c.get("colour") == u"\u2665"
        cards = standard_poker.search(lambda x: x.get("colour") == u"\u2663", number=4)
        assert len(cards) == 4
        cards = standard_poker.search(lambda x: x.get("colour") == u"\u2663", number=30)
        assert len(cards) == 8

    def test_search_query(self, standard_poker):
        cards = standard_poker.search("facevalue == 'A'")
        assert len(cards) == 4
        cards = standard_poker.search("colour == '\u2663'")
        assert len(cards) == 12

    def test_deal(self, standard_poker):
        hands = standard_poker.deal(4, 2)
        assert len(hands) == 4
        for h in hands:
            assert len(h) == 2

    def test_deal_too_many(self, standard_poker):
        hands = standard_poker.deal(30, 2)
        assert len(hands) == 30
