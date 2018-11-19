import pytest

from gagarin.core.zone import Component
from gagarin.core.parser import DslInterpreter


@pytest.fixture(scope="function")
def component():
    yield Component(name="toto", value=10)

@pytest.fixture(scope="module")
def interpreter():
    yield DslInterpreter()


class TestParser(object):

    def test_equals(self, interpreter, component):
        interpreter.attach(component)
        result = interpreter.interpret("""name == 'toto'""")
        assert result
        result = interpreter.interpret("""name == 'titi'""")
        assert not result
        result = interpreter.interpret("value == 11")
        assert not result
        result = interpreter.interpret("value == 10")
        assert result

    def test_or(self, interpreter, component):
        interpreter.attach(component)
        result = interpreter.interpret("name == 'tutu' or name == 'tata'")
        assert not result
        result = interpreter.interpret("name == 'tutu' or value == 10")
        assert result
        result = interpreter.interpret("name == 'toto' or value == 11")
        assert result

    def test_and(self, interpreter, component):
        interpreter.attach(component)
        result = interpreter.interpret("name == 'toto' and value == 11")
        assert not result
        result = interpreter.interpret("name == 'tutu' and value == 10")
        assert not result
        result = interpreter.interpret("name == 'toto' and value == 10")
        assert result

    def test_differs(self, interpreter, component):
        interpreter.attach(component)
        result = interpreter.interpret("name != 'toto'")
        assert not result
        result = interpreter.interpret("name != 'tutu'")
        assert result

    def test_greater(self, interpreter, component):
        interpreter.attach(component)
        result = interpreter.interpret("11 > 10 > 9")
        assert result
        result = interpreter.interpret("value >= 10")
        assert result
        result = interpreter.interpret("value > 9")
        assert result
        result = interpreter.interpret("value >= 11")
        assert not result
        result = interpreter.interpret("value > 10")
        assert not result
        result = interpreter.interpret("value > -10.2")
        assert result
        result = interpreter.interpret("value >= 9.99")
        assert result

    def test_lower(self, interpreter, component):
        interpreter.attach(component)
        result = interpreter.interpret("1 <= 2 <= 3")
        assert result
        result = interpreter.interpret("1 < 4 < 5")
        assert result
        result = interpreter.interpret("1 < 2 <= 2")
        assert result
        result = interpreter.interpret("value <= 10")
        assert result
        result = interpreter.interpret("value < 11")
        assert result
        result = interpreter.interpret("value <= 9")
        assert not result
        result = interpreter.interpret("value < 10")
        assert not result
        result = interpreter.interpret("8 < value <= 11")
        assert result
        result = interpreter.interpret("12 > value <= 15")
        assert result
        result = interpreter.interpret("12 > value <= 8")
        assert not result

    def test_in(self, interpreter, component):
        interpreter.attach(component)
        result = interpreter.interpret("name in ['toto', 'tutu', 'tata']")
        assert result
        result = interpreter.interpret("name in ['tutu', 'tata', -12.13]")
        assert not result
        result = interpreter.interpret("name in [['tutu', 'tata'], -12.13]")
        assert not result
        result = interpreter.interpret("name in [{'tutu', 'tata'}, 'toto']")
        assert result

    def test_like(self, interpreter, component):
        interpreter.attach(component)
        result = interpreter.interpret("name like 'tot?'")
        assert result
        result = interpreter.interpret("name like '*to'")
        assert result
        result = interpreter.interpret("name like 'tata'")
        assert not result
        result = interpreter.interpret("name like 12.34")
        assert not result

    def test_parenthesis(self, interpreter, component):
        interpreter.attach(component)
        result = interpreter.interpret("(name == 'tutu' and value <= 10) or (name == 'toto' and value > 5)")
        assert result

    def test_maths(self, interpreter, component):
        interpreter.attach(component)
        result = interpreter.interpret("1 + 2 == 3")
        assert result
        result = interpreter.interpret("2 * 3 == 6")
        assert result
        result = interpreter.interpret("2 - 3 == -1")
        assert result
        result = interpreter.interpret("1.0 / 2.0 == 0.5")
        assert result
        result = interpreter.interpret("1 + 2 * 3 == 7")
        assert result
        result = interpreter.interpret("(1 + 2) * 3 == 9")
        assert result
        result = interpreter.interpret("1 + (2 * 3) == 7")
        assert result
        result = interpreter.interpret("(1 + 2) * (5 - 3) == 1 + (3 * 2) - 1")
        assert result
        result = interpreter.interpret("3 * (1 - (6 / 3 + 2)) == -9")
        assert result
        result = interpreter.interpret("3 * 1 - 6 / 3 + 2 == 3")
        assert result
