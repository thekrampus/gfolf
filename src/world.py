import src.game

from pyglet.gl import *
from pyglet import resource

_MAP_SIZE_ = 256
_WATER_ = 1
_LAND_ = 0

class World():
    def __init__(self):
        self.terrain = resource.image(src.game._RES_PATH_ + "gfolfzone.png")

        with open(src.game._RES_PATH_ + "gfolf_water.data", 'rb') as fdat:
            self.water_map = bytearray(fdat.read())


    def bg_render(self):
        self.background.blit(0, 0)
        
    def render(self):
        terrain_tex = self.terrain.get_texture()
        glEnable(terrain_tex.target)
        glBindTexture(terrain_tex.target, terrain_tex.id)
        glTexParameteri(terrain_tex.target, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glBegin(GL_TRIANGLE_FAN)
        glTexCoord2f(0.0, 5.0); glVertex3f(0, 0, 0)
        glTexCoord2f(5.0, 5.0); glVertex3f(5*_MAP_SIZE_, 0, 0)
        glTexCoord2f(5.0, 0.0); glVertex3f(5*_MAP_SIZE_, 0, 5*_MAP_SIZE_)
        glTexCoord2f(0.0, 0.0); glVertex3f(0, 0, 5*_MAP_SIZE_)
        glEnd()
        glDisable(terrain_tex.target)

    def on_land(self, x, y):
        lin_map = (int(y) % _MAP_SIZE_) * _MAP_SIZE_ + (int(x) % _MAP_SIZE_)
        return (self.water_map[lin_map] == _LAND_)
        
