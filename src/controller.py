from pyglet.window import key

_BUTTON_MAP_ = {key.LEFT   : 'left',
                key.RIGHT  : 'right',
                key.UP     : 'up',
                key.DOWN   : 'down',
                key.ESCAPE : 'menu',
                key.SPACE  : 'action'}

# Stateless buttons don't "repeat fire" when held down
_STATELESS_BUTTONS_ = ['menu', 'action']

class GameController:
    def __init__(self):
        self.state = {}
        self.function = {}
        for button in _BUTTON_MAP_.values():
            self.state[button] = False

    def press(self, key):
        if key in _BUTTON_MAP_:
            button = _BUTTON_MAP_[key]
            if button in _STATELESS_BUTTONS_:
                self.fire(button)
            else:
                self.state[button] = True

    def release(self, key):
        if key in _BUTTON_MAP_:
            button = _BUTTON_MAP_[key]
            self.state[button] = False

    def get_state(self, button):
        if button in self.state:
            return self.state[button]
        else:
            return None

    def hook_function(self, button, function):
        self.function[button] = function

    def fire(self, button):
        if self.function[button]:
            self.function[button]()

    def fire_all(self):
        for button in [b for b in self.state if self.state[b] and self.function[b]]:
            self.function[button]()
