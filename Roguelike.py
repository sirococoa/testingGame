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
            if -self.w <= self.x - other.x <= other.w:
                if -self.h <= self.y - other.y <= other.h:
                    return True
            return False

        def length(self, other):
            buffer = 0
            if self.x < other.x:
                buffer += other.x - (self.x + self.w)
            else:
                buffer += self.x - (other.x + other.w)
            if self.y < other.y:
                buffer += other.y - (self.y + self.h)
            else:
                buffer += self.y - (other.y + other.h)
            return buffer

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