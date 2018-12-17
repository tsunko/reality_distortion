from math import sqrt
from enum import Enum


# why this instead of math.isclose?
# math.isclose accounts for _relative_ differences by performing multiplication
# performance with python and floating point mult is _terrible_.
# therefore, use a way less accurate version that is substantially faster
def _vector2_isclose(f1: float, f2: float, allowed_error=0.5):
    return abs(f2 - f1) < allowed_error


# helper function to double check if any operations being done is
# being done with two vectors
def _vector2_check_type(other):
    if not isinstance(other, Vector2):
        raise TypeError


class Direction(Enum):
    EAST = 0
    SOUTH_EAST = 1
    SOUTH = 2
    SOUTH_WEST = 3
    WEST = 4
    NORTH_WEST = 5
    NORTH = 6
    NORTH_EAST = 7

    def __invert__(self):
        return INVERT_DIRECTION[self]


INVERT_DIRECTION = {
    Direction.EAST: Direction.WEST,
    Direction.SOUTH_EAST: Direction.NORTH_WEST,
    Direction.SOUTH: Direction.NORTH,
    Direction.SOUTH_WEST: Direction.NORTH_EAST,
    Direction.WEST: Direction.EAST,
    Direction.NORTH_WEST: Direction.SOUTH_EAST,
    Direction.NORTH: Direction.SOUTH,
    Direction.NORTH_EAST: Direction.SOUTH_WEST
}


class Vector2:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def distance(self, other, squared=False) -> float:
        # perform calculations by using the numerical values directly
        # rather than relying on arithmetic operators, which create a new Vector2
        # which is really bad for constant calls
        dx = other.x - self.x
        dy = other.y - self.y
        if squared:
            return dx * dx + dy * dy
        else:
            return sqrt(dx * dx + dy * dy)

    def to_iso(self):
        return Vector2(self.x - self.y, (self.x + self.y) / 2)

    def to_2d(self):
        return Vector2((2 * self.y + self.x) / 2, (2 * self.y - self.x) / 2)

    def clone(self):
        return Vector2(self.x, self.y)

    def normalize(self):
        length = sqrt(self.x * self.x + self.y * self.y)
        if length == 0:
            return Vector2(0, 0)
        return Vector2(self.x / length, self.y / length)

    def __add__(self, other) -> 'Vector2':
        _vector2_check_type(other)
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other) -> 'Vector2':
        _vector2_check_type(other)
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, other) -> 'Vector2':
        _vector2_check_type(other)
        return Vector2(self.x * other.x, self.y * other.y)

    def __truediv__(self, other) -> 'Vector2':
        _vector2_check_type(other)
        return Vector2(self.x / other.x, self.y / other.y)

    def __floordiv__(self, other) -> 'Vector2':
        _vector2_check_type(other)
        return Vector2(self.x // other.x, self.y // other.y)

    def __pow__(self, other, modulo=None) -> 'Vector2':
        _vector2_check_type(other)
        return Vector2(self.x ** other.x, self.y ** other.y)

    def __le__(self, other):
        _vector2_check_type(other)
        return self.x <= other.x and self.y <= other.y

    def __lt__(self, other):
        _vector2_check_type(other)
        return self.x < other.x and self.y < other.y

    def __ge__(self, other):
        _vector2_check_type(other)
        return self.x >= other.x and self.y >= other.y

    def __gt__(self, other):
        _vector2_check_type(other)
        return self.x > other.x and self.y > other.y

    def __eq__(self, other):
        _vector2_check_type(other)
        return _vector2_isclose(self.x, other.x) and _vector2_isclose(self.y, other.y)

    def __repr__(self):
        return "Vector2(%.2f, %.2f)" % (self.x, self.y)

    def __neg__(self) -> 'Vector2':
        return Vector2(-self.x, -self.y)

    def __hash__(self):
        return hash((self.x, self.y))
