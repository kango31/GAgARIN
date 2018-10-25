import pytest

from siolib.core.die import Face, Die


@pytest.fixture(scope="function")
def die6():
    faces = [ ]
    for v in [1, 2, 3, 4, 5, 6]:
        faces.append(Face(value=v))
    yield Die(faces, color="Blue")


class TestDie(object):
    def test__gettattr__01(self, die6):
        assert die6.get("color") == "Blue"

    def test_number_of_sides(self, die6):
        assert die6.number_of_sides() == 6

    def test_roll(self, die6):
        for i in range(100):
            value = die6.roll().get("value")
            assert (1 <= value <= 6)

    def test_visible_face(self, die6):
        assert die6.get_visible_face().get("value") == 1
        value = die6.roll().get("value")
        assert value == die6.get_visible_face().get("value")
        die6.set_visible_face(lambda x: x.get("value") == 3).get_visible_face().get("value") == 3
