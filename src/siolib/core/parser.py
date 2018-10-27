"""
Implement a Domain Specific Language for string queries

https://www.youtube.com/watch?v=tSwITbXRe8M&index=1&list=PLBOh8f9FoHHgPEbiK-FSdSw3FiyP78fbk
https://www.youtube.com/watch?v=hvdj-xCgz_M&index=2&list=PLBOh8f9FoHHgPEbiK-FSdSw3FiyP78fbk
https://www.youtube.com/watch?v=P5ovtpvHsEA&list=PLBOh8f9FoHHgPEbiK-FSdSw3FiyP78fbk&index=3
"""

import fnmatch
import operator

from sly import Lexer, Parser


class DslLexer(Lexer):
    tokens = {
            NAME,
            FLOAT, INT, STRING,
            AND, OR,
            EQUALS, DIFFERS,
            GREATER_THAN, GREATER_EQUAL, LOWER_THAN, LOWER_EQUAL,
            COMMA, IN, LIKE
    }
    ignore = ' \t'
    literals = { '[', ']', '{', '}', '(', ')', '+', '*', '-', '/'}

    # Tokens
    AND = r'and'
    OR = r'or'
    COMMA = r','
    IN = r'in'
    LIKE = r'like'

    NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'

    @_(r'-?\d+\.\d*')
    def FLOAT(self, t):
        t.value = float(t.value)
        return t

    @_(r'-?\d+')
    def INT(self, t):
        t.value = int(t.value)
        return t

    STRING = r"""['].*?[']|["].*?["]"""

    EQUALS = r'=='
    DIFFERS = r'!='
    GREATER_EQUAL = r'>='
    GREATER_THAN = r'>'
    LOWER_EQUAL = r'<='
    LOWER_THAN = r'<'

    @_(r'\n+')
    def newline(self, t):
        self.lineno += t.value.count('\n')

    def error(self, t):
        raise SyntaxError("Illegal character '%s'" % t.value[0])
        self.index += 1


class DslParser(Parser):
    tokens = DslLexer.tokens

    precedence = (
        ('left', 'OR'),
        ('left', 'AND'),
        ('left', 'EQUALS', 'DIFFERS',
         'GREATER_THAN', 'GREATER_EQUAL', 'LOWER_THAN', 'LOWER_EQUAL'),
        ('left', '+', '-'),
        ('left', '*', '/'),
    )

    def attach(self, component):
        self.component = component

    @_('condition')
    def statement(self, p):
        return p[0]

    @_('NAME')
    def expr(self, p):
        return self.component.get(p.NAME)

    @_('INT')
    def expr(self, p):
        return p.INT

    @_('FLOAT')
    def expr(self, p):
        return p.FLOAT

    @_('STRING')
    def expr(self, p):
        #Get rid of quotes
        return p.STRING[1:-1]

    @_('arglist COMMA expr',
       'expr')
    def arglist(self, p):
        if len(p) == 1:
            return [p[0]]
        else:
            p[0].append(p[2])
            return p[0]

    @_('"[" arglist "]"',
       '"{" arglist "}"')
    def sequence(self, p):
        return p[1]

    @_('sequence')
    def expr(self, p):
        return p.sequence

    @_('expr IN sequence')
    def condition(self, p):
        return p.expr in p.sequence

    @_('expr EQUALS expr')
    def condition(self, p):
        return p.expr0 == p.expr1

    @_('expr DIFFERS expr')
    def condition(self, p):
        return p.expr0 != p.expr1

    @_('comp_expr GREATER_EQUAL expr',
       'comp_expr GREATER_THAN expr',
       'comp_expr LOWER_EQUAL expr',
       'comp_expr LOWER_THAN expr',
       'expr GREATER_EQUAL expr',
       'expr GREATER_THAN expr',
       'expr LOWER_EQUAL expr',
       'expr LOWER_THAN expr')
    def comp_expr(self, p):
        if p[1] == ">=":
            op = operator.ge
        elif p[1] == ">":
            op = operator.gt
        elif p[1] == "<=":
            op = operator.le
        elif p[1] == "<":
            op = operator.lt
        try:
            return op(p.expr0, p.expr1), p.expr1
        except:
            return p.comp_expr[0] and op(p.comp_expr[1], p.expr), p.expr

    @_('comp_expr')
    def condition(self, p):
        return p.comp_expr[0]

    @_('condition OR condition')
    def condition(self, p):
        return p.condition0 or p.condition1

    @_('condition AND condition')
    def condition(self, p):
        return p.condition0 and p.condition1

    @_('"(" condition ")"')
    def condition(self, p):
        return p.condition

    @_('expr LIKE expr')
    def condition(self, p):
        return fnmatch.fnmatch(str(p.expr0), str(p.expr1))

    @_('expr "+" expr')
    def expr(self, p):
        return p.expr0 + p.expr1

    @_('expr "-" expr')
    def expr(self, p):
        return p.expr0 - p.expr1

    @_('expr "*" expr')
    def expr(self, p):
        return p.expr0 * p.expr1

    @_('expr "/" expr')
    def expr(self, p):
        return p.expr0 / p.expr1

    @_('"(" expr ")"')
    def expr(self, p):
        return p.expr

if __name__ == '__main__':
    lexer = DslLexer()
    parser = DslParser()
    while True:
        try:
            text = input('calc > ')
        except EOFError:
            break
        if text:
            parser.parse(lexer.tokenize(text))
