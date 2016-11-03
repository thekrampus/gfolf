import src.game
from src.blinker import Blinker

from pyglet.gl import *
from pyglet import resource, text, clock

_CAMERA_HEIGHT_ = 1.5
_CAMERA_DIST_ = 4.3
_PITCH_LIMITS_ = (0, 25)


def ortho_start(dim):
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, dim[0], 0, dim[1])
    glMatrixMode(GL_MODELVIEW)

def ortho_end(dim):
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def gl_init():
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

def tuple_diff(a, b):
    return tuple(p[0] - p[1] for p in zip(a, b))

class Camera:
    def __init__(self, width, height):
        self.background = resource.image(src.game._RES_PATH_ + "vista_bg.png")
        self.rpy = (0, 2, 0)
        self.refresh(width, height)
        self.dimension = (width, height)

        gl_init()

    def translate(self, pos):
        glTranslatef(-pos[0], -_CAMERA_HEIGHT_, -pos[1])

    def rotate(self):
        glTranslatef(0, 0, -_CAMERA_DIST_)
        
        glRotatef(self.rpy[1], 1, 0, 0)
        glRotatef(self.rpy[2], 0, 1, 0)
        glRotatef(self.rpy[0], 0, 0, 1)

    def billboard_rotate(self):        
        glRotatef(self.rpy[2], 0, -1, 0)

    def routine(self, world, main_player, other_players, items):
        glClear(GL_COLOR_BUFFER_BIT)

        self.draw_bg()

        glPushMatrix()
        glLoadIdentity()

        self.rotate()

        self.translate(main_player.pos)

        world.render()
            
        glPopMatrix()

        glPushMatrix()
        glLoadIdentity()
        self.rotate()
        for p in other_players:
            glPushMatrix()
            self.translate(tuple_diff(main_player.pos, p.pos))
            self.billboard_rotate()
            p.bg_render()
            glPopMatrix()
        for i in items:
            glPushMatrix()
            self.translate(tuple_diff(main_player.pos, i.pos))
            self.billboard_rotate()
            i.render()
            glPopMatrix()
        glPopMatrix()
            
        self.draw_main_player(main_player)

    def draw_bg(self):
        ortho_start(self.dimension)

        self.background.blit(-1800 + (360 - self.rpy[2])*5, self.rpy[1]*8)

        ortho_end(self.dimension)

    def draw_main_player(self, main_player):
        ortho_start(self.dimension)

        main_player.main_render(self.dimension[0], self.dimension[1])

        Blinker.try_draw()
        
        ortho_end(self.dimension)

    def draw_billboard(self, image, pos):
        glPushMatrix()
        glRotatef(self.rpy[0], 0, 0, 1)
        self.translate(pos)

        image.blit(0, 0)
        
        glPopMatrix()
        
    def refresh(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(65, width/float(height), .1, 1000)
        glMatrixMode(GL_MODELVIEW)

        self.dimension = (width, height)
        
    def move(self, dRpy):
        new_pitch = self.rpy[1] - dRpy[1]
        if new_pitch < _PITCH_LIMITS_[0] or new_pitch > _PITCH_LIMITS_[1]:
            dRpy = (dRpy[0], 0, dRpy[2])
        self.rpy = tuple((p[0] - p[1]) % 360 for p in zip(self.rpy, dRpy))

    def set(self, newRpy):
        self.rpy = newRpy
