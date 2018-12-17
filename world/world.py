from typing import List
from vector import Vector2, Direction
from PIL import Image
from shape import Rectangle
import logging
import sys


_log = logging.getLogger(__name__)


class Zone(Rectangle):
    def __init__(self, name: str, p1: Vector2, p2: Vector2):
        super(Zone, self).__init__(p1, p2)
        self.name = name
        self.neighbors = {
            Direction.NORTH: None,
            Direction.EAST: None,
            Direction.SOUTH: None,
            Direction.WEST: None
        }

    def get_open_directions(self) -> List[Direction]:
        return [direction for direction in self.neighbors.keys() if self.neighbors[direction] is None]

    def get_neighbors(self) -> List['Zone']:
        return [zone for zone in self.neighbors.values() if zone is not None]

    def overlaps(self, other: 'Zone') -> bool:
        return self.bottom_left.x < other.top_right.x and \
               self.bottom_left.y < other.top_right.y and \
               self.top_right.x > other.bottom_left.x and \
               self.top_right.y > other.bottom_left.y

    def width(self) -> int:
        return self.top_right.x - self.bottom_left.x

    def height(self) -> int:
        return self.top_right.y - self.bottom_left.y

    def center(self) -> Vector2:
        return Vector2(self.bottom_left.x + self.width() / 2,
                       self.bottom_left.y + self.height() / 2)


class World:
    def __init__(self, zones: List[Zone]):
        self.zones = zones
        self.entities = list()
        self.real_big_same = self._world_generate_map()
        self.dump_world()

    def tick_world(self, dt):
        for entity in self.entities:
            entity.tick_entity(dt)
        self.entities[:] = [entity for entity in self.entities if entity.health > 0]

    def get_zone_containing_point(self, point: Vector2) -> Zone:
        if point.x < self.min_pos.x or point.y < self.min_pos.y or \
           point.x > self.max_pos.x or point.y > self.max_pos.y:
            return None

        index_x, index_y = self._world_fix_point(point)
        return self.real_big_same[index_y][index_x]

    def get_zones(self) -> List[Zone]:
        return self.zones

    def _world_generate_map(self) -> List[List[Zone]]:
        _log.info("Starting internal map generation...")
        self.max_pos = Vector2(sys.float_info.min, sys.float_info.min)
        self.min_pos = Vector2(sys.float_info.max, sys.float_info.max)

        for zone in self.zones:
            self.max_pos.x = max(zone.top_right.x, self.max_pos.x)
            self.max_pos.y = max(zone.top_right.y, self.max_pos.y)

            self.min_pos.x = min(zone.bottom_left.x, self.min_pos.x)
            self.min_pos.y = min(zone.bottom_left.y, self.min_pos.y)

        rows = int(self.max_pos.x - self.min_pos.x)
        columns = int(self.max_pos.y - self.min_pos.y)

        _log.setLevel(10)
        _log.debug("Using map stats:")
        _log.debug("min_pos: %s", repr(self.min_pos))
        _log.debug("max_pos: %s", repr(self.max_pos))
        _log.debug("rows x columns: %d x %d", rows, columns)

        map = [[None for _ in range(rows)] for _ in range(columns)]  # type: List[List[Zone]]
        for y in range(int(self.max_pos.y) - 1, int(self.min_pos.y), -1):
            for x in range(int(self.min_pos.x), int(self.max_pos.x) - 1):
                point = Vector2(x, y)
                index_x, index_y = int(x + abs(self.min_pos.x)), int(y + abs(self.min_pos.y))
                for zone in self.zones:
                    if point in zone:
                        map[index_y][index_x] = zone
                        break

        _log.info("Finished internal map generation.")
        return map

    def _world_fix_point(self, point: Vector2):
        # fixes any point into within game world bounds
        x = int(point.x + abs(self.min_pos.x)) - 1
        y = int(point.y + abs(self.min_pos.y)) - 1
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        return x, y

    def dump_world(self):
        # dumps the current world as a .png file
        img = Image.new("RGB", (self.width(), self.height()))
        for y in range(self.height()):
            for x in range(self.width()):
                point = Vector2(self.max_pos.x - x, self.max_pos.y - y)
                zone = self.get_zone_containing_point(point)
                if zone is not None:
                    img.putpixel((x, y), (128, 128, 128))
        img.save("world.png")

    def width(self):
        return int(self.max_pos.x - self.min_pos.x)

    def height(self):
        return int(self.max_pos.y - self.min_pos.y)

    def __contains__(self, point):
        return self.get_zone_containing_point(point) is not None
