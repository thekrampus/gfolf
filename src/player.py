import src.game
from src.blinker import Blinker

from pyglet.gl import *
from pyglet import image, sprite, clock, text

from math import sin, cos, sqrt, radians

_SPRITES_ = {'gray'   : 'gfolfer.png',
             'cyan'   : 'gfolfer_cyan.png',
             'orange' : 'gfolfer_orange.png'}

_ANIM_STATE_ = {'aiming'    : 0,
                'adjusting' : 3,
                'powering'  : 3,
                'shooting'  : 8,
                'watching'  : 0,
                'post'      : 0,
                'exploding' : 0}
_FRAME_DELAY_ = 4

_CHARACTER_DIM_ = (94, 170)

_STATES_ = ['aiming', 'adjusting', 'powering', 'shooting', 'watching', 'exploding', 'paused', 'post']

class Player():
    def __init__(self, pos=(128, 128), color='gray'):
        raw_sprite = image.load(src.game._RES_PATH_ + _SPRITES_[color])
        self.spritesheet = image.ImageGrid(raw_sprite, 1, 9)
        explosion_anim = image.load_animation(src.game._RES_PATH_ + 'dope_explosion.gif')
        self.explosion_sprite = sprite.Sprite(explosion_anim)
        
        self.color = color
        
        self.shot = Shot(pos)
        self.state = 'aiming'
        self.anim_i = 0
        self.frame_delay = 0
        
        self.pos = pos
        self.health = 100

        self.health_ui = text.Label('',
                                    font_name = 'Andale Mono',
                                    font_size = 18,
                                    color=(238, 19, 19, 255),
                                    x=20, y=20,
                                    anchor_x='left', anchor_y='center')
        
    def main_render(self, width, height):
        # Render as main character
        cx = width/2 - _CHARACTER_DIM_[0]
        cy = height/2 - _CHARACTER_DIM_[1]

        if self.state == 'post' or self.state == 'exploding':
            self.explosion_sprite.set_position(cx + 50, cy-50)
            self.explosion_sprite.draw()
        elif self.state != 'watching':
            self.spritesheet[self.anim_i].blit(cx, cy)
            self.ui_render()
            self.shot.render(cx, cy)
        else:
            self.shot.render(cx, cy)

        if self.frame_delay == 0:
            if self.anim_i != _ANIM_STATE_[self.state]:
                self.anim_i  = (self.anim_i + 1) % len(self.spritesheet)
                self.frame_delay = _FRAME_DELAY_
        else:
            self.frame_delay -= 1

    def update(self, dt, other_players):
        if self.state == 'watching':
            self.pos = self.shot.compute_shot(dt)
            self.check_collisions(other_players)
            
    def bg_render(self):
        # Render as background character
        if self.state == 'exploding':
            # TODO: This is a nightmare
            self.explosion_sprite.draw()
            i = self.explosion_sprite._frame_index
            tex = self.explosion_sprite.image.frames[i].image.get_texture()
        else:
            tex = self.spritesheet[0].get_texture()
            
        glEnable(tex.target)
        glBindTexture(tex.target, tex.id)
        glTexParameteri(tex.target, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(tex.target, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glBegin(GL_TRIANGLE_FAN)
        glTexCoord2f(0.0, 0.0); glVertex3f(-1.0, 0, 0)
        glTexCoord2f(0.0, 1.0); glVertex3f(-1.0, 3.0, 0)
        glTexCoord2f(1.0, 1.0); glVertex3f(2.0, 3.0, 0)
        glTexCoord2f(1.0, 0.0); glVertex3f(2.0, 0, 0)
        glEnd()
        glDisable(tex.target)

    def ui_render(self):
        self.health_ui.text = '<3 ' + str(self.health) + '%'
        self.health_ui.draw()
        
        if self.state == 'adjusting':
            self.shot.build_adjust_label().draw()
        elif self.state == 'powering':
            self.shot.build_power_label().draw()

    def is_dead(self):
        return self.health <= 0

    def move(self, dPos):
        self.pos = tuple(sum(p) for p in zip(self.pos, dPos))

    def start_aiming(self):
        self.state = 'aiming'
        
    def start_adjusting(self, angle):
        self.state = 'adjusting'
        self.shot = Shot(self.pos, angle)
        clock.schedule_interval(self.shot.inc_adjust, Shot.ADJUST_PERIOD)

    def start_powering(self):
        self.state = 'powering'
        clock.unschedule(self.shot.inc_adjust)
        clock.schedule_interval(self.shot.inc_power, Shot.POWER_PERIOD)

    def start_shot(self):
        self.state = 'shooting'
        clock.unschedule(self.shot.inc_power)

    def watch_shot(self):
        self.state = 'watching'

    def start_exploding(self, damage):
        if self.state != 'exploding':
            Blinker.start_message('GOT EM', 3)
            self.health -= damage
            self.state = 'exploding'
        
    def end_turn(self, on_land):
        self.state = 'post'
        if on_land:
            Blinker.start_message('NNNICE', 1)
            self.pos = self.shot.compute_endpt()
        else:
            Blinker.start_message('WASTED', 1, color=Blinker._PALETTE_['blue'])
            self.pos = self.shot.compute_endpt()
            clock.schedule_once(self.revert_shot, 1.6)
            self.health = self.health // 2 + 1

    def revert_shot(self, dt=0):
        self.pos = self.shot.origin

    def check_collisions(self, other_players):
        # TODO: Just... ugh
        for p in other_players:
            if src.game.distance(self.pos, p.pos) <= 1:
                p.start_exploding(self.shot.curved_power() // 2 + 1)
        
class Shot:
    MAX_ADJUST = 31
    ADJUST_PERIOD = 1/50
    MAX_POWER = 30
    POWER_PERIOD = 1/100
    TRAVEL_SECONDS = 5
    TRAVEL_TIME = 60*TRAVEL_SECONDS
    
    def __init__(self, origin, angle=0):
        self.sprite = image.load(src.game._RES_PATH_ + 'gfolfball.png')
        
        self.origin = origin
        self.angle = angle
        self.adjustment = 10
        self.power = 5
        self.increment = 1
        self.travel_i = 0

        self.meter = text.Label('',
                                font_name = 'Andale Mono',
                                font_size = 18,
                                x=600, y=100,
                                anchor_x='center', anchor_y='center')

    def set_angle(self, angle):
        self.angle = angle
        
    def inc_adjust(self, dt=0):
        if self.adjustment >= Shot.MAX_ADJUST or self.adjustment <= 0:
            self.increment *= -1
        self.adjustment += self.increment

    def inc_power(self, dt=0):
        if self.power >= Shot.MAX_POWER or self.power <= 0:
            self.increment *= -1
        self.power += self.increment
        
    def build_adjust_label(self):
        s = '[' + ' ' * (self.adjustment) + 'I' + ' ' * (Shot.MAX_ADJUST - self.adjustment) + ']'
        self.meter.text = s
        return self.meter
        

    def build_power_label(self):
        s = '[' + '>' * (self.power) + ' ' * (Shot.MAX_POWER - self.power) + ']'
        self.meter.text = s
        return self.meter
    
    def compute_shot(self, dt):
        # print('dt: ' + str(dt))
        shot_angle = self.angle + 4*(self.adjustment - 15)
        amp = self.curved_power() * (self.travel_i/Shot.TRAVEL_SECONDS)
        endpoint = (self.origin[0] + sin(radians(shot_angle)) * amp,
                    self.origin[1] - cos(radians(shot_angle)) * amp)
        self.travel_i += dt
        # self.travel_i += 1
        return endpoint

    def compute_endpt(self):
        self.travel_i = Shot.TRAVEL_SECONDS
        return self.compute_shot(0)

    def curved_power(self):
        return float(((self.power + 5)/3)**2)

    def render(self, cx, cy):
        dy = cy*(2 - (self.travel_i/(Shot.TRAVEL_SECONDS/2) - 1)**2) + 5
        self.sprite.blit(cx+85, dy)
        
