from vector import Vector2


# basic rectangle used for many things
class Rectangle:
    def __init__(self, p1: Vector2, p2: Vector2):
        self.bottom_left = Vector2(min(p1.x, p2.x), min(p1.y, p2.y))
        self.top_right = Vector2(max(p1.x, p2.x), max(p1.y, p2.y))
        self.color = (128, 128, 128)

    def __contains__(self, point):
        if isinstance(point, Vector2):
            return self.bottom_left.x <= point.x <= self.top_right.x and \
                   self.bottom_left.y <= point.y <= self.top_right.y
        else:
            raise TypeError