from random import randrange

import pyxel


class RogueLike:
    def __init__(self):
        pass

    def update(self):
        pass

    def draw(self):
        pass


class Stage:
    class Room:
        def __init__(self, width, height, min_size, max_size):
            while True:
                self.x = randrange(0, width)
                self.y = randrange(0, height)
                self.w = randrange(min_size, max_size)
                self.h = randrange(min_size, max_size)
                if self.x + self.w <= width and self.y + self.h <= height:
                    break

        def collision(self, other):
            pass

    def __init__(self, width, height, max_room_num):
        self.width = width
        self.height = height
        self.max_room_num = max_room_num
        self.make_stage()

    def make_stage(self):
        pass

    def draw(self):
        pass


if __name__ == '__main__':
    RogueLike()