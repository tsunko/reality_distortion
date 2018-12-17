from vector import Vector2 as v2, Direction
from world.world import World, Zone
from random import randint, choice
from typing import List
import logging

_log = logging.getLogger(__name__)


class WorldGenerator:
    def __init__(self, room_count: int,
                 min_size: v2, max_size: v2,
                 round_to: int):
        self.count = room_count
        self.min_size = min_size
        self.max_size = max_size
        self.round_to = round_to

    def generate(self) -> World:
        _log.info("Starting world generation...")
        zones = []
        zones_left = self.count

        while zones_left > 0:
            if not zones:
                gen_bottom_left = v2(_worldgen_round(-self.min_size.x * 0.75, self.round_to),
                                     _worldgen_round(-self.min_size.y * 0.75, self.round_to))
                gen_top_right = v2(_worldgen_round(self.min_size.x * 0.75, self.round_to),
                                   _worldgen_round(self.min_size.y * 0.75, self.round_to))
                generated_zone = Zone("starting-room", gen_bottom_left, gen_top_right)
            else:
                gen_width = _worldgen_round(randint(self.min_size.x, self.max_size.x), self.round_to)
                gen_height = _worldgen_round(randint(self.min_size.y, self.max_size.y), self.round_to)
                # legacy docs below: pypy doesn't have a 3.6 version, so choices() doesn't exist
                # choices() allows weighting
                # by default, k=1, so choices() will only have 1 element (safe to just use [0])
                # the weighting I chose to use was just using the amount of open neighbors to the 10th
                # why to the 10th? I want a significantly less chance of it picking a zone with 3 neighbors as opposed
                # to one with just 1 neighbor. obviously, I should probably just use squared or something
                # but I really _really_ don't want 4-way corridors.
                random_parent_zone = choice(zones)
                open_directions = random_parent_zone.get_open_directions()
                if not open_directions:
                    continue
                random_direction = choice(open_directions)
                offset_func = choice(_WORLDGEN_OFFSET[random_direction])
                bottom_left, top_right = offset_func(random_parent_zone, gen_width, gen_height, 0)

                generated_zone = Zone("zone-%d" % (self.count - zones_left), bottom_left, top_right)
                # if we generated an overlap, just discard it and generate another one
                if _worldgen_has_collision(zones, generated_zone):
                    continue
                random_parent_zone.neighbors[random_direction] = generated_zone
                generated_zone.neighbors[~random_direction] = random_parent_zone

            zones.append(generated_zone)
            zones_left -= 1

        _log.info("Finished world generation!")
        return World(zones)


# rounds to nearest "to"
def _worldgen_round(num: int, to: int):
    return num + (to - num) % to


# check if world has collision with zone
def _worldgen_has_collision(zones: List[Zone], zone: Zone):
    for other_zone in zones:
        if zone.overlaps(other_zone):
            return True
    return False


# Here be dragons. All offset functions.

def _worldgen_offset_n_l(z: Zone, new_width: int, new_height: int, offset: int):
    return v2(z.bottom_left.x, z.top_right.y - offset), \
           v2(z.bottom_left.x + new_width, z.top_right.y + new_height - offset)


def _worldgen_offset_n_m(z: Zone, new_width: int, new_height: int, offset: int):
    return v2(z.bottom_left.x + (z.width() / 2) - (new_width / 2), z.top_right.y - offset), \
           v2(z.bottom_left.x + (z.width() / 2) + (new_width / 2), z.top_right.y + new_height - offset)


def _worldgen_offset_n_r(z: Zone, new_width: int, new_height: int, offset: int):
    return v2(z.bottom_left.x + z.width() - new_width, z.top_right.y - offset), \
           v2(z.bottom_left.x + z.width(), z.top_right.y + new_height - offset)


def _worldgen_offset_e_t(z: Zone, new_width: int, new_height: int, offset: int):
    return v2(z.bottom_left.x + z.width() - offset, z.top_right.y), \
           v2(z.bottom_left.x + z.width() + new_width - offset, z.top_right.y - new_height)


def _worldgen_offset_e_m(z: Zone, new_width: int, new_height: int, offset: int):
    return v2(z.bottom_left.x + z.width() - offset, z.top_right.y - (z.height() / 2) + (new_height / 2)), \
           v2(z.bottom_left.x + z.width() + new_width - offset, z.top_right.y - (z.height() / 2) - (new_height / 2))


def _worldgen_offset_e_b(z: Zone, new_width: int, new_height: int, offset: int):
    return v2(z.bottom_left.x + z.width() - offset, z.top_right.y - z.height()), \
           v2(z.bottom_left.x + z.width() + new_width - offset, z.top_right.y - z.height() + new_height)


def _worldgen_offset_s_l(z: Zone, new_width: int, new_height: int, offset: int):
    return v2(z.bottom_left.x, z.top_right.y - z.height() + offset), \
           v2(z.bottom_left.x + new_width, z.top_right.y - z.height() - new_height  + offset)


def _worldgen_offset_s_m(z: Zone, new_width: int, new_height: int, offset: int):
    return v2(z.bottom_left.x + (z.width() / 2) - (new_width / 2), z.top_right.y - z.height()  + offset), \
           v2(z.bottom_left.x + (z.width() / 2) + (new_width / 2), z.top_right.y - z.height() - new_height  + offset)


def _worldgen_offset_s_r(z: Zone, new_width: int, new_height: int, offset: int):
    return v2(z.bottom_left.x + z.width() - new_width, z.top_right.y - z.height() + offset), \
           v2(z.bottom_left.x + z.width(), z.top_right.y - z.height() - new_height + offset)


def _worldgen_offset_w_t(z: Zone, new_width: int, new_height: int, offset: int):
    return v2(z.bottom_left.x + offset, z.top_right.y), \
           v2(z.bottom_left.x - new_width + offset, z.top_right.y - new_height)


def _worldgen_offset_w_m(z: Zone, new_width: int, new_height: int, offset: int):
    return v2(z.bottom_left.x + offset, z.top_right.y - (z.height() / 2) + (new_height / 2)), \
           v2(z.bottom_left.x - new_width + offset, z.top_right.y - (z.height() / 2) - (new_height / 2))


def _worldgen_offset_w_b(z: Zone, new_width: int, new_height: int, offset: int):
    return v2(z.bottom_left.x + offset, z.top_right.y - z.height()), \
           v2(z.bottom_left.x - new_width + offset, z.top_right.y - z.height() + new_height)


_WORLDGEN_OFFSET = {
    Direction.NORTH: [
        _worldgen_offset_n_l,
        _worldgen_offset_n_m,
        _worldgen_offset_n_r
    ],
    Direction.EAST: [
        _worldgen_offset_e_t,
        _worldgen_offset_e_m,
        _worldgen_offset_e_b
    ],
    Direction.SOUTH: [
        _worldgen_offset_s_l,
        _worldgen_offset_s_m,
        _worldgen_offset_s_r
    ],
    Direction.WEST: [
        _worldgen_offset_w_t,
        _worldgen_offset_w_m,
        _worldgen_offset_w_b
    ]
}