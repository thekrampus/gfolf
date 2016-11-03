from pyglet import text, clock

class Blinker():
    _PERIOD_ = 1/2
    _PALETTE_ = {'white' : (255, 255, 255, 255),
                 'red'   : (238,  19,  19, 255),
                 'blue'  : ( 11, 151, 228, 255),
                 'cyan'  : (107, 255, 255, 255),
                 'orange': (255, 155,  57, 255)}
    
    _is_on = False
    _label = text.Label('',
                        font_name = 'Arial',
                        font_size = 72,
                        italic=True, bold=True,
                        x=600, y=400,
                        anchor_x='center', anchor_y='center')

    @classmethod
    def start_message(cls, text, duration, color=_PALETTE_['white']):
        cls.set_state(True)
        cls._label.text = text
        cls._label.color = color
        timesteps = int(duration / Blinker._PERIOD_)
        for i in range(timesteps):
            clock.schedule_once(lambda dt: cls.set_state(True), Blinker._PERIOD_ * 2 * i)
            clock.schedule_once(lambda dt: cls.set_state(False), Blinker._PERIOD_ * (2 * i + 1))

    @classmethod
    def set_label(cls, label):
        cls._label = label

    @classmethod
    def set_state(cls, state):
        cls._is_on = state

    @classmethod
    def try_draw(cls):
        if cls._is_on:
            cls._label.draw()
