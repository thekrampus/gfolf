from src.world import World
from src.camera import Camera
from src.controller import GameController
from src.player import Player, Shot
from src.blinker import Blinker
from src.pickup import Stapler

from pyglet import app, window, clock, text

from random import randrange
from math import sqrt

_FRAME_RATE_ = 1/60
_MOVE_SPEED_ = 2
_RES_PATH_ = "res/"


def distance(a, b):
    return sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

class Game(window.Window):
    def __init__(self):
        super(Game, self).__init__(1200, 600, caption='WELCOME 2 GFOLF')
        self.world = World()
        self.cam = Camera(1200, 600)

        self.init_players()
        self.init_items(60, 3)
        
        self.controller = GameController()
        self.start_aiming()

    def init_players(self):
        sep = (randrange(10, 15), randrange(10, 15))
        o = (600, 660)

        self.players = []
        self.double_turn = False
        self.players.append(Player(pos=(o[0] + sep[0], o[1] + sep[1]), color='cyan'))
        self.players.append(Player(pos=(o[0] - sep[0], o[1] - sep[1]), color='orange'))

    def init_items(self, density, quantity):
        o = (600, 660)

        locations = [(o[0] + randrange(-density, density), o[1] + randrange(-density, density)) for _ in range(quantity)]
        self.items = [Stapler(pos=x) for x in locations]
        
    def on_draw(self):
        self.cam.routine(self.world, self.players[0], self.players[1:], self.items)

        Blinker.try_draw()
        
    def on_key_press(self, symbol, modifiers):
        self.controller.press(symbol)

    def on_key_release(self, symbol, modifiers):
        self.controller.release(symbol)

    def on_resize(self, width, height):
        self.cam.refresh(width, height)
        
    def run(self):
        clock.schedule_interval(self.update, _FRAME_RATE_)
        Blinker.start_message('GFOLF', 5)
        app.run()

    def update(self, dt):
        self.controller.fire_all()
        self.get_main_player().update(dt, self.players[1:])
        for i in self.items:
            i.check_collision(self.get_main_player())

    def add_player(self, player):
        self.players.append(player)
            
    def get_main_player(self):
        return self.players[0]

    def start_aiming(self, dt=0):
        self.get_main_player().start_aiming()
        self.controller.hook_function('menu', self.close)
        self.controller.hook_function('left', lambda: self.cam.move((0, 0, _MOVE_SPEED_)))
        self.controller.hook_function('right', lambda: self.cam.move((0, 0, -_MOVE_SPEED_)))
        self.controller.hook_function('up', lambda: self.cam.move((0, 1, 0)))
        self.controller.hook_function('down', lambda: self.cam.move((0, -1, 0)))
        self.controller.hook_function('action', self.start_adjusting)

    def start_adjusting(self):
        self.get_main_player().start_adjusting(self.cam.rpy[2])
        self.controller.hook_function('left', None)
        self.controller.hook_function('right', None)
        self.controller.hook_function('up', None)
        self.controller.hook_function('down', None)
        self.controller.hook_function('action', self.start_powering)

    def start_powering(self):
        self.get_main_player().start_powering()
        self.controller.hook_function('action', self.start_shot)

    def start_shot(self):
        self.get_main_player().start_shot()
        self.controller.hook_function('action', None)
        clock.schedule_once(self.watch_shot, 2)

    def watch_shot(self, dt=0):
        self.get_main_player().watch_shot()
        clock.schedule_once(self.end_shot, Shot.TRAVEL_SECONDS)
        
    def end_shot(self, dt=0):
        pos = self.get_main_player().pos
        on_land = self.world.on_land(pos[0], pos[1])
        self.get_main_player().end_turn(on_land)
        clock.schedule_once(self.next_turn, 1.5)
        
    def next_turn(self, dt=0):
        self.purge_dead()

        if len(self.players) > 1:
            self.get_main_player().start_aiming()
            if not self.double_turn:
                self.players = self.players[1:] + [self.players[0]]
            else:
                self.double_turn = False
            color = Blinker._PALETTE_[self.get_main_player().color]
            Blinker.start_message('OK GO', 2, color)
            clock.schedule_once(self.start_aiming, 2)
        else:
            self.post_game()
            
    def post_game(self):
        color = Blinker._PALETTE_[self.get_main_player().color]
        Blinker.start_message('YOU DID IT', 10, color)
        clock.schedule(lambda dt: self.cam.move((0, -0.1, -0.4)))

    def purge_dead(self):
        self.players = [p for p in self.players if not p.is_dead()]
        
        for i in [i for i in self.items if not i.active]:
            i.despawn(self)
        self.items = [i for i in self.items if i.active]
