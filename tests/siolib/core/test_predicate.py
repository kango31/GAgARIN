import pytest

from siolib.core.predicate import Predicate
from siolib.core.zone import Component


@pytest.fixture(scope="function")
def component():
    yield Component(name="toto", value=10)


class TestComponent(object):
    def test_query(self, component):
        pred = Predicate("name == 'toto'")
        assert pred(component)
        pred = Predicate("name == 'titi'")
        assert not pred(component)
        pred = Predicate("1 <= value <= 10")
        assert pred(component)
        with pytest.raises(NameError):
            pred = Predicate("1 <= Value <= 10")
            pred(component)

    def test_func(self, component):
        pred = Predicate(lambda x: x.get("name") == "toto")
        assert pred(component)
