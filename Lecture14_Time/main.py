from pico2d import *
import game_framework

import play_mode as start_mode

open_canvas(1600, 600,sync=True)
game_framework.run(start_mode)
close_canvas()

