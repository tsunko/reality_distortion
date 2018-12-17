from world.world import World, Zone
from vector import Vector2 as v2
from entity import Entity
from typing import List
import pyglet


# helper method to convert to tuples
def _rendering_v2_to_tup(*v2s):
    ret = ()
    for vec in v2s:
        iso = vec.to_iso()
        ret += (iso.x, iso.y)
    return ret

# convert zone to v2f for rendering with opengl
def _rendering_zone_to_v2f(z: Zone):
    bottom_left = z.bottom_left
    bottom_right = v2(z.top_right.x, z.bottom_left.y)
    top_right = z.top_right
    top_left = v2(z.bottom_left.x, z.top_right.y)

    return _rendering_v2_to_tup(bottom_left, bottom_right, top_right, top_left)


def draw_world(world: World):
    world_batch = pyglet.graphics.Batch()
    for zone in world.zones:
        # draw zones by converting them to v2f tuples
        zone_drawing = _rendering_zone_to_v2f(zone)
        world_batch.add(4, pyglet.gl.GL_QUADS, None,
                        ('v2f', zone_drawing),
                        ('c3B', zone.color * 4))
    world_batch.draw()


def draw_entities(entities: List[Entity]):
    entity_batch = pyglet.graphics.Batch()
    for entity in entities:
        # draw entities as 10 pixel wide dots on the screen
        pyglet.gl.glPointSize(10)
        entity_batch.add(1, pyglet.gl.GL_POINTS, None,
                         ('v2f', _rendering_v2_to_tup(entity.position)),
                         ('c3B', entity.color))
    entity_batch.draw()

def draw_ui(screen_width, screen_height, world: World, player: Entity):
    # create ui batch
    ui_batch = pyglet.graphics.Batch()
    scale = 150
    # calculate health pixel height
    health_ui_height = (player.health / player.maximum_health) * scale
    health_border = 2
    # add health background
    ui_batch.add(4, pyglet.gl.GL_QUADS, None,
                 ('v2f', (0, 0,
                          scale + health_border, 0,
                          scale + health_border, scale + health_border,
                          0, scale + health_border)),
                 ('c3B', (128, 128, 32) * 4))
    # add actual health
    ui_batch.add(4, pyglet.gl.GL_QUADS, None,
                 ('v2f', (0, 0,
                          scale, 0,
                          scale, health_ui_height,
                          0, health_ui_height)),
                 ('c3B', (200, 0, 0) * 4))
    ui_batch.draw()
