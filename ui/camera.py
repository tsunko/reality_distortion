from vector import Vector2
from pyglet.gl import *


class Camera:
    def __init__(self, screen_width: int, screen_height: int, zoom: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.position = Vector2(0, 0)
        self.zoom = zoom

    # initialize orthographic view and use 0,0 as the center of the screen
    # if we don't need 0,0 as center, then 0,0 is bottom left
    def initialize_ortho(self, origin_is_center=True):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        if origin_is_center:
            glOrtho(-self.screen_width/2, self.screen_width/2, -self.screen_height/2, self.screen_height/2, -1, 1)
        else:
            glOrtho(0, self.screen_width, 0, self.screen_height, -1, 1)

    # fake "movement" by simply shifting camera
    def translate_with_position(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(-self.position.x, -self.position.y, 0)
        glScalef(self.zoom, self.zoom, 0)

    # resets identity and restores old 0,0-bottom-left view
    def reset_identity(self):
        glLoadIdentity()
        self.initialize_ortho(False)
