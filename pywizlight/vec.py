"""Helper class with some math.

    A bunch of utility functions, just so we don't have to bring in any external dependencies.
"""
from math import cos, sin, sqrt
from operator import add, mul, sub
from typing import Tuple

# a small value, really close to zero, more than adequate for our 3 orders of magnitude
# of color resolution
EPSILON = 1.0e-5

Vector = Tuple[float, ...]
IntVector = Tuple[int, ...]


def vecDot(a: Vector, b: Vector) -> float:
    """Retrun sum."""
    return sum(map(mul, a, b))


def vecLenSq(a: Vector) -> float:
    """Return the vector's magnitude squared."""
    return vecDot(a, a)


def vecLen(a: Vector) -> float:
    """Return the vector's magnitude."""
    lenSq = vecLenSq(a)
    return sqrt(lenSq) if (lenSq > EPSILON) else 0


def vecAdd(a: Vector, b: Vector) -> Vector:
    """Sum two vectors."""
    return tuple(map(add, a, b))


def vecSub(a: Vector, b: Vector) -> Vector:
    """Subtract two vectors."""
    return tuple(map(sub, a, b))


def vecMul(vec: Vector, sca: float) -> Vector:
    """Scale a vector."""
    return tuple(c * sca for c in vec)


def vecInt(vec: Vector) -> IntVector:
    """Truncate the vector to integer precision."""
    return tuple(map(int, vec))


def vecNormalize(vec: Vector) -> Vector:
    """Normalize the vector (i.e. make its magnitude 1)."""
    vector_length = vecLen(vec)
    return vecMul(vec, 1 / vector_length) if (vector_length > EPSILON) else vec


def vecFormat(vec: Vector) -> str:
    """Retruns something."""
    return f"({str([float(f'{n:.3f}') for n in vec])[1:-1]})"


def vecFromAngle(angle: float) -> Vector:
    """Return the unit vector for a given angle (in radians)."""
    return (cos(angle), sin(angle))
