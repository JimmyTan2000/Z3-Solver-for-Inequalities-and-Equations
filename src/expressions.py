from z3 import *
from pcomb import *


# Combined parser for boolean and arithmetic expressions
class ParseExpr(Parser):
    def __init__(self):
        self.parser = ParseBExpr() ^ ParseArithExpr()


# Arithmetic Expressions
class ParseArithExpr(Parser):
    def __init__(self):
        self.parser = ParsePlus() ^ ParseTerm()


class ParseTerm(Parser):
    def __init__(self):
        self.parser = ParseTimes() ^ ParseFactor()


class ParseFactor(Parser):
    def __init__(self):
        self.parser = ParseParen() ^ ParseCon() ^ ParseVar()


class ParsePlus(Parser):
    def __init__(self):
        self.parser = ParseTerm()      >> (lambda t:
                      ParseSymbol('+') >> (lambda _:
                      ParseArithExpr()      >> (lambda e:
                      Return(Plus(t, e)))))


class ParseTimes(Parser):
    def __init__(self):
        self.parser = ParseFactor()    >> (lambda x:
                      ParseSymbol('*') >> (lambda _:
                      ParseTerm()      >> (lambda y:
                      Return(Times(x, y)))))


class ParseParen(Parser):
    def __init__(self):
        self.parser = ParseSymbol('(') >> (lambda _:
                      ParseArithExpr()      >> (lambda e:
                      ParseSymbol(')') >> (lambda _:
                      Return(e))))


class ParseCon(Parser):
    def __init__(self):
        self.parser = ParseInt() >> (lambda n:
                      Return(Con(n)))


class ParseVar(Parser):
    def __init__(self):
        self.parser = ParseIdent() >> (lambda name:
                      Return(Var(name)))


class Expr:
    def __add__(self, other):
        return Plus(self, other)

    def __mul__(self, other):
        return Times(self, other)


class Con(Expr):
    def __init__(self, val):
        self.val = val

    def __str__(self):
        return str(self.val)

    def ev(self, env):
        return self.val

    def __eq__(self, other):
        if type(other).__name__ != "Con":
            return False
        return self.val == other.val

    def vars_(self):
        return []

    def toZ3(self):
        return self.val


class Var(Expr):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def ev(self, env):
        return env[self.name]

    def __eq__(self, other):
        if type(other).__name__ != "Var":
            return False
        return self.name == other.name

    def toZ3(self):
        return Int(f"{self.name}")


class BinOp(Expr):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self):
        return f"({self.left} {self.op} {self.right})"

    def ev(self, env):
        return self.fun(self.left.ev(env), self.right.ev(env))

    def __eq__(self, other):
        if not isinstance(other, BinOp):
            return False
        return self.name == other.name and self.left == other.left and self.right == other.right

    def vars_(self):
        return list(set(self.left.vars_() + self.right.vars_()))

    def toZ3(self):
        pass


class Plus(BinOp):
    name = "Plus"
    fun = lambda _, x, y: x + y
    op = '+'

    def toZ3(self):
        return self.left.toZ3() + self.right.toZ3()


class Times(BinOp):
    name = "Times"
    fun = lambda _, x, y: x * y
    op = '*'

    def toZ3(self):
        return self.left.toZ3() * self.right.toZ3()


# Boolean Expressions
class ParseBExpr(Parser):
    def __init__(self):
        self.parser = ParseOr() ^ ParseDisj()


class ParseDisj(Parser):
    def __init__(self):
        self.parser = ParseAnd() ^ ParseConj()


class ParseConj(Parser):
    def __init__(self):
        self.parser = ParseCmp() ^ ParseBParen()


class ParseBVar(Parser):
    def __init__(self):
        self.parser = ParseIdentifier() >> (lambda name:
                      Return(BVar(name)))


class ParseBParen(Parser):
    def __init__(self):
        self.parser = ParseSymbol("(") >> (lambda _:
                      ParseBExpr() >> (lambda e:
                      ParseSymbol(")") >> (lambda _:
                      Return(e))))


class ParseOr(Parser):
    def __init__(self):
        self.parser = ParseDisj() >> (lambda d:
                      ParseSymbol("or") >> (lambda _:
                      ParseBExpr() >> (lambda e:
                      Return(BOr(d, e)))))


class ParseAnd(Parser):
    def __init__(self):
        self.parser = ParseConj() >> (lambda x:
                      ParseSymbol("and") >> (lambda _:
                      ParseDisj() >> (lambda y:
                      Return(BAnd(x, y)))))


class ParseCmp(Parser):
    def __init__(self):
        self.parser = ParseEq() ^ ParseLThan()


class ParseEq(Parser):
    def __init__(self):
        self.parser = (ParseArithExpr() >> (lambda x:
                      ParseSymbol("=") >> (lambda _:
                      ParseArithExpr() >> (lambda y:
                      Return(Eq(x, y))))))


class ParseLThan(Parser):
    def __init__(self):
        self.parser = (ParseArithExpr() >> (lambda x:
                      ParseSymbol("<") >> (lambda _:
                      ParseArithExpr() >> (lambda y:
                      Return(LThan(x, y))))))


class BExpr:
    pass


class BVar(BExpr):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def ev(self, env):
        return env[self.name]

    def toZ3(self):
        pass


class Op2(BExpr):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self):
        return f"({self.left} {self.op} {self.right})"

    def ev(self, env):
        return self.fun(self.left.ev(env), self.right.ev(env))

    def toZ3(self):
        pass


class BOr(Op2):
    op = "or"
    fun = lambda _, x, y: x or y

    def toZ3(self):
        return Or(self.left.toZ3(), self.right.toZ3())


class BAnd(Op2):
    op = "and"
    fun = lambda _, x, y: x and y

    def toZ3(self):
        return And(self.left.toZ3(), self.right.toZ3())


class Eq(Op2):
    op = "="
    fun = lambda _, x, y: x == y

    def toZ3(self):
        return self.left.toZ3() == self.right.toZ3()


class LThan(Op2):
    op = "<"
    fun = lambda _, x, y: x < y

    def toZ3(self):
        return self.left.toZ3() < self.right.toZ3()