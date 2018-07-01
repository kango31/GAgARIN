import pytest

from siolib.core.zone import Component, Zone


@pytest.fixture(scope="function")
def zone():
    yield Zone(name="Board")


@pytest.fixture(scope="function")
def component():
    yield Component(name="toto", value=10)

@pytest.fixture(scope="function")
def tree():
    board = Zone(name="Board")
    player1 = Zone(name="Player1")
    player2 = Zone(name="Player2")
    board.add(player1)
    board.add(player2)
    ressources1 = Zone(name="Ressources1")
    ressources2 = Zone(name="Ressources2")
    player1.add(ressources1)
    player2.add(ressources2)
    yield board


class TestComponent(object):
    def test_get(self, component):
        assert component.get("name") == "toto"
        assert component.get("value") == 10
        assert component.get("value", str) == "10"

    def test__getattr__(self, component):
        assert component.name == "toto"
        assert component.value == 10


class TestZone(object):
    def test_add(self, zone):
        assert len(zone) == 0
        component = Component()
        zone.add(component)
        assert len(zone) == 1

    def test_remove(self, zone):
        assert len(zone) == 0
        component = Component()
        zone.add(component)
        assert len(zone) == 1
        zone.remove(Component())
        assert len(zone) == 1
        zone.remove(component)
        assert len(zone) == 0

    def test_search_component(self, tree):
        assert tree.search_component(lambda x: x.name == "Board").name == "Board"
        assert tree.search_component(lambda x: x.name == "Player1").name == "Player1"
        assert tree.search_component(lambda x: x.name == "Ressources2").name == "Ressources2"
        assert tree.search_component(lambda x: x.name == "NonExisting") is None

    def test_apply(self, tree):
        class Transform(object):
            def __init__(self):
                self._transformed = [ ]

            def __call__(self, component):
                self._transformed.append(component)

            def __len__(self):
                return len(self._transformed)

            def clear(self):
                self._transformed = []
        transform = Transform()
        tree.apply(transform)
        assert len(transform) == 5
        transform.clear()
        tree.apply(transform, lambda x: x.name.startswith("Player"))
        assert len(transform) == 2
