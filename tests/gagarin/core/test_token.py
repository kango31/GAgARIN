import pytest

from gagarin.core.token import Token, OneSidedToken, TwoSidedToken, Face


@pytest.fixture(scope="function")
def token0():
	yield Token(color="yellow")


@pytest.fixture(scope="function")
def token1():
    yield OneSidedToken(value="+3")

@pytest.fixture(scope="function")
def token2():
    face1 = Face(symbol="Research")
    face2 = Face(symbol="Gold")
    yield TwoSidedToken(face1, face2, color="Grey")


class TestToken(object):
    def test__gettattr__01(self, token0):
        assert token0.get("color") == "yellow"

    def test__gettattr__02(self, token1):
        assert token1.get("value") is None
        assert token1.set_face_up(True).get("value") == "+3"

    def test_flip_01(self, token1):
        assert token1.get("value") is None
        assert token1.flip().get("value") == "+3"
        assert token1.set_face_up(False).get("value") is None
        assert token1.set_face_down(False).get("value") == "+3"

    def test_flip_02(self, token2):
        assert token2.get_visible_face().get("symbol") == "Research"
        assert token2.get("color") == "Grey"
        token2.flip()
        assert token2.get_visible_face().get("symbol") == "Gold"
        assert token2.get("color") == "Grey"
        token2.set_visible_face(lambda x: x.get("symbol") == "Research")
        assert token2.get_visible_face().get("symbol") == "Research"
        assert token2.get("color") == "Grey"
