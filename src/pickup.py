import src.game
from src.blinker import Blinker

from pyglet.gl import *
from pyglet import image, clock


class Pickup():
    def __init__(self, pos=(0, 0)):
        self.active = True
        self.pos = pos

    def render(self):
        tex = self.sprite.get_texture()
        glEnable(tex.target)
        glBindTexture(tex.target, tex.id)
        glTexParameteri(tex.target, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(tex.target, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glBegin(GL_TRIANGLE_FAN)
        glTexCoord2f(0.0, 0.0); glVertex3f(-1, 0.0, 0)
        glTexCoord2f(0.0, 1.0); glVertex3f(-1, 2.0, 0)
        glTexCoord2f(1.0, 1.0); glVertex3f(1, 2.0, 0)
        glTexCoord2f(1.0, 0.0); glVertex3f(1, 0.0, 0)
        glEnd()
        glDisable(tex.target)

    def check_collision(self, player):
        if self.active and src.game.distance(self.pos, player.pos) <= 1.5:
            self.active = False
            self.pick_up(player)

    def pick_up(self, player):
        pass
    
    def despawn(self):
        pass

class Stapler(Pickup):
    def __init__(self, pos=(0, 0)):
        super(Stapler, self).__init__(pos)
        self.sprite = image.load(src.game._RES_PATH_ + 'stapler.png')

    def pick_up(self, player):
        Blinker.start_message("NICE FUCKIN' STAPLER", 3)
        self.collector = player

    def despawn(self, game):
        game.double_turn = True
