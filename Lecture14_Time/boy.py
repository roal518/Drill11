# 이것은 각 상태들을 객체로 구현한 것임.
PIXEL_PER_METER = (10.0/0.3)
RUN_SPEED_KMPH = 20.0#시속 20km
RUN_SPEED_MPM = RUN_SPEED_KMPH*1000.0/60.0
RUN_SPEED_MPS = RUN_SPEED_MPM/60.0
RUN_SPEED_PPS = RUN_SPEED_MPS*PIXEL_PER_METER
TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0/TIME_PER_ACTION
FRAMES_PER_ACTION = 5
FRAMES_PER_TIME = ACTION_PER_TIME*FRAMES_PER_ACTION

## 시간을 고려해서 게임을 만들어야한다.***
from pico2d import get_time, load_image, load_font, clamp,  SDL_KEYDOWN, SDL_KEYUP, SDLK_SPACE, SDLK_LEFT, SDLK_RIGHT
from ball import Ball, BigBall
import game_world
import game_framework
import random

# state event check
# ( state event type, event value )

def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT


def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT


def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT


def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT

def space_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE

def time_out(e):
    return e[0] == 'TIME_OUT'
def Auto_run(e):
    return e[0] == 'AUTO_RUN'
# time_out = lambda e : e[0] == 'TIME_OUT'




# Boy Run Speed
# fill here

# Boy Action Speed
# fill here

class Idle:

    @staticmethod
    def enter(boy, e):
        if boy.face_dir == -1:
            boy.action = 2
        elif boy.face_dir == 1:
            boy.action = 3
        boy.dir = 0
        boy.frame = 0
        boy.wait_time = get_time() # pico2d import 필요
        pass

    @staticmethod
    def exit(boy, e):
        if space_down(e):
            boy.fire_ball()
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + FRAMES_PER_ACTION*ACTION_PER_TIME*game_framework.frame_time) % 5
        if get_time() - boy.wait_time > 2:
            boy.state_machine.handle_event(('TIME_OUT', 0))

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(int(boy.frame) * 183, 168, 167, 167, boy.x, boy.y)


class Auto:
    def enter(boy, e):
        if right_down(e) or left_up(e):  # 오른쪽으로 RUN
            boy.dir, boy.action, boy.face_dir = 1, 1, 1
        elif left_down(e) or right_up(e):  # 왼쪽으로 RUN
            boy.dir, boy.action, boy.face_dir = -1, 0, -1

    @staticmethod
    def exit(boy, e):
        if space_down(e):
            boy.fire_ball()
        pass

    @staticmethod
    def do(boy):
        if boy.is_turn == 1:
            boy.frame = (boy.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 5
            boy.x += 1 * RUN_SPEED_PPS * game_framework.frame_time
            boy.x = clamp(50, boy.x, 1600 - 50)
            if boy.x >= 1500:
                boy.is_turn = 0
        elif boy.is_turn == 0:
            boy.frame = (boy.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 5
            boy.x -= 1 * RUN_SPEED_PPS * game_framework.frame_time
            boy.x = clamp(50, boy.x, 1600 - 50)
            if boy.x <= 100:
                boy.is_turn = 1

    @staticmethod
    def draw(boy):
        if boy.is_turn == 1:
            boy.image.clip_draw(int(boy.frame) * 183, 168, 167, 167, boy.x, boy.y)
        elif boy.is_turn == 0:
            boy.image.clip_composite_draw(int(boy.frame) * 183, 168, 167, 167, 135,'v', boy.x, boy.y,167,167)


class StateMachine:
    def __init__(self, boy):
        self.boy = boy
        self.cur_state = Auto
        self.transitions = {
            Auto:{Auto_run:Auto}
        }

    def start(self):
        self.cur_state.enter(self.boy, ('AUTO_RUN', 0))

    def update(self):
        self.cur_state.do(self.boy)

    def handle_event(self, e):
        for check_event, next_state in self.transitions[self.cur_state].items():
            if check_event(e):
                self.cur_state.exit(self.boy, e)
                self.cur_state = next_state
                self.cur_state.enter(self.boy, e)
                return True

        return False

    def draw(self):
        self.cur_state.draw(self.boy)





class Boy:
    def __init__(self):
        self.x, self.y = random.randint(300,1200), random.randint(200,600)
        self.frame = 0
        self.action = 3
        self.face_dir = 1
        self.dir = 0
        self.image = load_image('bird_animation.png')
        self.font = load_font('ENCR10B.TTF',16)
        self.state_machine = StateMachine(self)
        self.state_machine.start()
        self.item = 'Ball'
        self.is_turn = 0

    def fire_ball(self):

        if self.item ==   'Ball':
            ball = Ball(self.x, self.y, self.face_dir*10)
            game_world.add_object(ball)
        elif self.item == 'BigBall':
            ball = BigBall(self.x, self.y, self.face_dir*10)
            game_world.add_object(ball)
        # if self.face_dir == -1:
        #     print('FIRE BALL LEFT')
        #
        # elif self.face_dir == 1:
        #     print('FIRE BALL RIGHT')

        pass

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        self.state_machine.handle_event(('INPUT', event))

    def draw(self):
        self.state_machine.draw()
        self.font.draw(self.x-80,self.y+50,f'{get_time()}',(255,255,0))
