#!encoding: utf-8

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


class AbstractSyntaxTree:
    def __init__(self, node, *args):
        """
        Constructor.

        :param node: node type
        :type node: str
        """
        self.node = node
        self.args = args

    def __str__(self):
        """
        Return a string reprensation of abstract syntax tree.

        :rtype: str
        """
        return "({}, {})".format(self.node, ", ".join(map(str, self.args)))


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

    def error(self, token):
        raise SyntaxError

    @_('condition')
    def statement(self, p):
        return AbstractSyntaxTree("stmt", p[0])

    @_('NAME')
    def expr(self, p):
        return AbstractSyntaxTree("get", p.NAME)

    @_('INT')
    def expr(self, p):
        return AbstractSyntaxTree('int', p.INT)

    @_('FLOAT')
    def expr(self, p):
        return AbstractSyntaxTree('float', p.FLOAT)

    @_('STRING')
    def expr(self, p):
        #Get rid of quotes
        return AbstractSyntaxTree('str', p.STRING[1:-1])

    @_('arglist COMMA expr',
       'expr')
    def arglist(self, p):
        if len(p) == 1:
            return AbstractSyntaxTree("arglist", [], p[0])
        else:
            return AbstractSyntaxTree("arglist", p[0], p[2])

    @_('"[" arglist "]"',
       '"{" arglist "}"')
    def sequence(self, p):
        return AbstractSyntaxTree("sequence", p[1])

    @_('sequence')
    def expr(self, p):
        return AbstractSyntaxTree("sequence", p.sequence)

    @_('expr IN sequence')
    def condition(self, p):
        return AbstractSyntaxTree("in", p.expr, p.sequence)

    @_('expr EQUALS expr')
    def condition(self, p):
        return AbstractSyntaxTree("==", p.expr0, p.expr1)

    @_('expr DIFFERS expr')
    def condition(self, p):
        return AbstractSyntaxTree("!=", p.expr0, p.expr1)

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
            return AbstractSyntaxTree("comp_expr", op, p.expr0, p.expr1)
        except KeyError:
            return AbstractSyntaxTree("comp_expr", op, p.comp_expr, p.expr)

    @_('comp_expr')
    def condition(self, p):
        return AbstractSyntaxTree("reduce_comp_expr", p.comp_expr)

    @_('condition OR condition')
    def condition(self, p):
        return AbstractSyntaxTree("or", p.condition0, p.condition1)

    @_('condition AND condition')
    def condition(self, p):
        return AbstractSyntaxTree("and", p.condition0, p.condition1)

    @_('"(" condition ")"')
    def condition(self, p):
        return AbstractSyntaxTree("self", p.condition)

    @_('expr LIKE expr')
    def condition(self, p):
        return AbstractSyntaxTree("match", p.expr0, p.expr1)

    @_('expr "+" expr')
    def expr(self, p):
        return AbstractSyntaxTree("+", p.expr0, p.expr1)

    @_('expr "-" expr')
    def expr(self, p):
        return AbstractSyntaxTree("-", p.expr0, p.expr1)

    @_('expr "*" expr')
    def expr(self, p):
        return AbstractSyntaxTree("*", p.expr0, p.expr1)

    @_('expr "/" expr')
    def expr(self, p):
        return AbstractSyntaxTree("/", p.expr0, p.expr1)

    @_('"(" expr ")"')
    def expr(self, p):
        return AbstractSyntaxTree("self", p.expr)


class DslInterpreter():
    def __init__(self, component=None):
        """
        Constructor.

        :param component: context component on which execution is made.
        :type component: Component
        """
        self._component = component

    def attach(self, component):
        """
        Attach component to intepreter to make interpretation context-dependent.

        :param component: context for interpretation
        :type component: Component
        """
        self._component = component

    def interpret(self, code):
        """
        Interpret the provided code in the current component context.

        :param code: code to be interpreted
        :type code: str
        :rtype: Python object
        """
        tokens = DslLexer().tokenize(code)
        ast = DslParser().parse(tokens)
        return self.execute(ast)

    def execute(self, ast):
        """
        Execute the abstract syntax tree.

        This method recursively interprets the abstract syntax tree to get a
        result.

        :param ast: abstract syntax tree generated by the parser
        :type ast: AbstractSyntaxTree
        :return: whatever is returned by execution
        :rtype: Python object
        """
        if not isinstance(ast, AbstractSyntaxTree):
            return ast

        if ast.node == "stmt":
            return self.execute(ast.args[0])
        elif ast.node == "get":
            return self._component.get(ast.args[0])
        elif ast.node == "int":
            return ast.args[0]
        elif ast.node == "float":
            return ast.args[0]
        elif ast.node == "str":
            return ast.args[0]
        elif ast.node == "arglist":
            args0 = self.execute(ast.args[0])
            args1 = self.execute(ast.args[1])
            args0.append(args1)
            return args0
        elif ast.node == "sequence":
            return self.execute(ast.args[0])
        elif ast.node == "in":
            return self.execute(ast.args[0]) in self.execute(ast.args[1])
        elif ast.node == "==":
            return self.execute(ast.args[0]) == self.execute(ast.args[1])
        elif ast.node == "!=":
            return self.execute(ast.args[0]) != self.execute(ast.args[1])
        elif ast.node == "comp_expr":
                arg1 = self.execute(ast.args[1])
                arg2 = self.execute(ast.args[2])
                try:
                    return ast.args[0](arg1, arg2), arg2
                except TypeError:
                    return arg1[0] and ast.args[0](arg1[1], arg2), arg2
        elif ast.node == "reduce_comp_expr":
                return self.execute(ast.args[0])[0]
        elif ast.node == "and":
            return self.execute(ast.args[0]) and self.execute(ast.args[1])
        elif ast.node == "or":
            return self.execute(ast.args[0]) or self.execute(ast.args[1])
        elif ast.node == "self":
            return self.execute(ast.args[0])
        elif ast.node == "match":
            arg0 = self.execute(ast.args[0])
            arg1 = self.execute(ast.args[1])
            return fnmatch.fnmatch(str(arg0), str(arg1))
        elif ast.node == "+":
            return self.execute(ast.args[0]) + self.execute(ast.args[1])
        elif ast.node == "-":
            return self.execute(ast.args[0]) - self.execute(ast.args[1])
        elif ast.node == "*":
            return self.execute(ast.args[0]) * self.execute(ast.args[1])
        elif ast.node == "/":
            return self.execute(ast.args[0]) / self.execute(ast.args[1])


if __name__ == '__main__':
    import readline

    readline.parse_and_bind('tab: complete')
    #readline.parse_and_bind('set editing-mode vi')

    interpreter = DslInterpreter()
    while True:
        try:
            text = input('dsl >>> ')
        except EOFError:
            break
        else:
            if text:
                try:
                    print(interpreter.interpret(text))
                except SyntaxError:
                    print("SyntaxError:", text)
