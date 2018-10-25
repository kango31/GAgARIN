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
        assert tree.search_component(lambda x: x.get("name") == "Board").get("name") == "Board"
        assert tree.search_component(lambda x: x.get("name") == "Player1").get("name") == "Player1"
        assert tree.search_component(lambda x: x.get("name") == "Ressources2").get("name") == "Ressources2"
        assert tree.search_component(lambda x: x.get("name") == "NonExisting") is None

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
        tree.apply(transform, lambda x: x.get("name").startswith("Player"))
        assert len(transform) == 2

    def test_iter(self, tree):
        count = 0
        for child in tree:
            count += 1
        assert count == 2

    def test_search_all_components(self, tree):
        all = tree.search_all_components(lambda x: x.get("name").endswith("1"))
        assert all[0].get("name") == "Player1"
        assert all[1].get("name") == "Ressources1"
        all = tree.search_all_components()
        assert len(all) == 5

    def test_search_all_components_predicate(self, tree):
        all = tree.search_all_components("name == 'Player1'")
        assert all[0].get("name") == "Player1"

    def test_apply_predicate(self, tree):
        class Transform():
            def __init__(self):
                self.names = set()
            def __call__(self, component):
                self.names.add(component.get("name"))
        t = Transform()
        tree.apply(t, "name in ['Player1', 'Player2']")
        assert t.names == {'Player1', 'Player2'}
        t = Transform()
        tree.apply(t, "name.startswith('Play')")
        assert t.names == {'Player1', 'Player2'}
