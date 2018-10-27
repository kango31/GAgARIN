import pytest

from siolib.core.zone import Component
from siolib.core.parser import DslLexer, DslParser


@pytest.fixture(scope="function")
def component():
    yield Component(name="toto", value=10)

@pytest.fixture(scope="module")
def lexer():
    yield DslLexer()

@pytest.fixture(scope="module")
def parser():
    yield DslParser()


class TestParser(object):
    # def test_get_property(self, lexer, parser, component):
    #     parser.attach(component)
    #     result = parser.parse(lexer.tokenize("name"))
    #     assert result == "toto"
    #     result = parser.parse(lexer.tokenize("value"))
    #     assert result == 10
    #     result = parser.parse(lexer.tokenize("'hello world!'"))
    #     assert result == "hello world!"


    def test_equals(self, lexer, parser, component):
        parser.attach(component)
        result = parser.parse(lexer.tokenize("""name == 'toto'"""))
        assert result
        result = parser.parse(lexer.tokenize("""name == 'titi'"""))
        assert not result
        result = parser.parse(lexer.tokenize("value == 11"))
        assert not result
        result = parser.parse(lexer.tokenize("value == 10"))
        assert result

    def test_or(self, lexer, parser, component):
        parser.attach(component)
        result = parser.parse(lexer.tokenize("name == 'tutu' or name == 'tata'"))
        assert not result
        result = parser.parse(lexer.tokenize("name == 'tutu' or value == 10"))
        assert result
        result = parser.parse(lexer.tokenize("name == 'toto' or value == 11"))
        assert result

    def test_and(self, lexer, parser, component):
        parser.attach(component)
        result = parser.parse(lexer.tokenize("name == 'toto' and value == 11"))
        assert not result
        result = parser.parse(lexer.tokenize("name == 'tutu' and value == 10"))
        assert not result
        result = parser.parse(lexer.tokenize("name == 'toto' and value == 10"))
        assert result

    def test_differs(self, lexer, parser, component):
        parser.attach(component)
        result = parser.parse(lexer.tokenize("name != 'toto'"))
        assert not result
        result = parser.parse(lexer.tokenize("name != 'tutu'"))
        assert result

    def test_greater(self, lexer, parser, component):
        parser.attach(component)
        result = parser.parse(lexer.tokenize("11 > 10 > 9"))
        assert result
        result = parser.parse(lexer.tokenize("value >= 10"))
        assert result
        result = parser.parse(lexer.tokenize("value > 9"))
        assert result
        result = parser.parse(lexer.tokenize("value >= 11"))
        assert not result
        result = parser.parse(lexer.tokenize("value > 10"))
        assert not result
        result = parser.parse(lexer.tokenize("value > -10.2"))
        assert result
        result = parser.parse(lexer.tokenize("value >= 9.99"))
        assert result

    def test_lower(self, lexer, parser, component):
        parser.attach(component)
        result = parser.parse(lexer.tokenize("1 <= 2 <= 3"))
        assert result
        result = parser.parse(lexer.tokenize("1 < 4 < 5"))
        assert result
        result = parser.parse(lexer.tokenize("1 < 2 <= 2"))
        assert result
        result = parser.parse(lexer.tokenize("value <= 10"))
        assert result
        result = parser.parse(lexer.tokenize("value < 11"))
        assert result
        result = parser.parse(lexer.tokenize("value <= 9"))
        assert not result
        result = parser.parse(lexer.tokenize("value < 10"))
        assert not result
        result = parser.parse(lexer.tokenize("8 < value <= 11"))
        assert result
        result = parser.parse(lexer.tokenize("12 > value <= 15"))
        assert result
        result = parser.parse(lexer.tokenize("12 > value <= 8"))
        assert not result

    def test_in(self, lexer, parser, component):
        parser.attach(component)
        result = parser.parse(lexer.tokenize("name in ['toto', 'tutu', 'tata']"))
        assert result
        result = parser.parse(lexer.tokenize("name in ['tutu', 'tata', -12.13]"))
        assert not result
        result = parser.parse(lexer.tokenize("name in [['tutu', 'tata'], -12.13]"))
        assert not result
        result = parser.parse(lexer.tokenize("name in [{'tutu', 'tata'}, 'toto']"))
        assert result

    def test_like(self, lexer, parser, component):
        parser.attach(component)
        result = parser.parse(lexer.tokenize("name like 'tot?'"))
        assert result
        result = parser.parse(lexer.tokenize("name like '*to'"))
        assert result
        result = parser.parse(lexer.tokenize("name like 'tata'"))
        assert not result
        result = parser.parse(lexer.tokenize("name like 12.34"))
        assert not result

    def test_parenthesis(self, lexer, parser, component):
        parser.attach(component)
        result = parser.parse(lexer.tokenize("(name == 'tutu' and value <= 10) or (name == 'toto' and value > 5)"))
        assert result

    def test_maths(self, lexer, parser, component):
        parser.attach(component)
        result = parser.parse(lexer.tokenize("1 + 2 == 3"))
        assert result
        result = parser.parse(lexer.tokenize("2 * 3 == 6"))
        assert result
        result = parser.parse(lexer.tokenize("2 - 3 == -1"))
        assert result
        result = parser.parse(lexer.tokenize("1.0 / 2.0 == 0.5"))
        assert result
        result = parser.parse(lexer.tokenize("1 + 2 * 3 == 7"))
        assert result
        result = parser.parse(lexer.tokenize("(1 + 2) * 3 == 9"))
        assert result
        result = parser.parse(lexer.tokenize("1 + (2 * 3) == 7"))
        assert result
        result = parser.parse(lexer.tokenize("(1 + 2) * (5 - 3) == 1 + (3 * 2) - 1"))
        assert result
        result = parser.parse(lexer.tokenize("3 * (1 - (6 / 3 + 2)) == -9"))
        assert result
        result = parser.parse(lexer.tokenize("3 * 1 - 6 / 3 + 2 == 3"))
        assert result
