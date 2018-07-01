import pytest

from siolib.core.card import Card


@pytest.fixture(scope="function")
def card01():
	yield Card(facevalue="Ace", color="Spades")

class TestCard(object):
    def test_flip(self, card01):
    	assert card01.is_face_up()
    	card01.flip()
    	assert card01.is_face_down()

    def test_set_face(self, card01):
    	card01.set_face_up(True)
    	assert card01.is_face_up()
    	assert not card01.is_face_down()
    	card01.set_face_up(False)
    	assert not card01.is_face_up()
    	assert card01.is_face_down()

    def test__getattr__(self, card01):
    	assert card01.facevalue == "Ace"
    	assert card01.color == "Spades"
    	card01.set_face_up(False)
    	assert card01.facevalue is None
    	assert card01.color is None

    def test__setattr__(self, card01):
    	with pytest.raises(AttributeError):
    		card01.facevalue = "King"

    def test_chaining(self, card01):
    	card01.set_face_up(True).rotate(90).untap().flip()
    	assert card01.is_face_down()
    	assert card01.get_rotation() == 0

    def test_rotate(self, card01):
    	card01.rotate(45)
    	assert card01.get_rotation() == 45
    	card01.rotate(45)
    	assert card01.get_rotation() == 90

    def test_tap(self, card01):
    	assert card01.is_tapped() is False
    	assert card01.is_untapped()
    	card01.tap()
    	assert card01.is_tapped()
    	assert card01.is_untapped() is False
    	card01.untap()

