from expressions import *


def printExpr(inp):
    """
    >>> printExpr("x = y")
    (x = y)
    >>> printExpr("x + 2 * y")
    (x + (2 * y))
    >>> printExpr("x < 2 and y < 1")
    ((x < 2) and (y < 1))
    >>> printExpr("(x + 2*y < 15 + x * x) or z = 5")
    (((x + (2 * y)) < (15 + (x * x))) or (z = 5))
    >>> printExpr("x + 2*y < 15 + x * x or z = 5")
    (((x + (2 * y)) < (15 + (x * x))) or (z = 5))
    """
    print(result(ParseExpr().parse(inp)))


def evalExpr(inp, env):
    """
    >>> env = {'x':1, 'y':2, 'z':3}
    >>> evalExpr("x = y", env)
    False
    >>> evalExpr("x + 2 * y", env)
    5
    >>> evalExpr("x < 2 and y < 1", env)
    False
    >>> evalExpr("(x + 2*y < 15 + x * x) or z = 5", env)
    True
    >>> evalExpr("x + 2*y < 15 + x * x or z = 5", env)
    True
    >>> evalExpr("x * 2 + 3 < x * (2 + 3)", env)
    False
    >>> evalExpr("y * 2 + 3 < y * (2 + 3)", env)
    True
    """
    return result(ParseExpr().parse(inp)).ev(env)


def solve(lstinp):
    """
    >>> sol = solve(["x + y +z = 10", "x < y", "x < 3", "5 < x"])
    No solution!
    """
    s = Solver()
    for expr in lstinp:
        x = result(ParseExpr().parse(expr)).toZ3()
        s.add(x)
    if s.check() == sat:
        ans = str(s.model())
        ansStr = ans[1:-1]
        ansLst = ansStr.split(", ")
        ansSet = set()
        ansSet.update(ansLst)
        return ansSet
    else:
        print("No solution!")
        return None


