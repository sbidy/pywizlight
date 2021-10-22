"""Helper class with some math.

    A bunch of utility functions, just so we don't have to bring in any external dependencies.
"""
from math import sqrt, sin, cos
from operator import mul, sub, add


# a small value, really close to zero, more than adequate for our 3 orders of magnitude
# of color resolution
EPSILON = 1.0e-5


def vecDot(a, b):
    """Retrun sum."""
    return sum(map(mul, a, b))


def vecLenSq(a):
    """Retrun Square."""
    return vecDot(a, a)


def vecLen(a) -> float:
    """Retrun Square length."""
    lenSq = vecLenSq(a)
    return sqrt(lenSq) if (lenSq > EPSILON) else 0


def vecAdd(a, b) -> tuple:
    """Retrun tuple object with add."""
    return tuple(map(add, a, b))


def vecSub(a, b):
    """Retruns something."""
    return tuple(map(sub, a, b))


def vecMul(vec, sca):
    """Retruns something."""
    return tuple([c * sca for c in vec])


def vecInt(vec):
    """Retruns something."""
    return tuple([int(c) for c in vec])


def vecNormalize(vec):
    """Retruns something."""
    len = vecLen(vec)
    return vecMul(vec, 1 / len) if (len > EPSILON) else vec


def vecFormat(vec) -> str:
    """Retruns something."""
    return "({})".format(str([float("{0:.3f}".format(n)) for n in vec])[1:-1])


def vecFromAngle(angle):
    """Retruns something."""
    return (cos(angle), sin(angle))
