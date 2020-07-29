from random import randrange
from itertools import combinations

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
            self.coll = False

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

    def __init__(self, width, height, max_room_num, min_room_size, max_room_size):
        self.width = width
        self.height = height
        self.max_room_num = max_room_num
        self.min_room_size = min_room_size
        self.max_room_size = max_room_size
        self.make_stage()

    def make_stage(self):
        self.room_list = [Stage.Room(self.width, self.height, self.min_room_size, self.max_room_size) for _ in range(self.max_room_num)]
        for a, b in combinations(self.room_list, 2):
            if a.collision(b):
                b.coll = True
        self.room_list = [room for room in self.room_list if not room.coll]

        self.data = [[1 for _ in range(self.width)] for _ in range(self.height)]
        for room in self.room_list:
            for x in range(room.x + 1, room.x + room.w):
                for y in range(room.y + 1, room.y + room.h):
                    self.data[x][y] = 0

    def draw(self):
        pass


if __name__ == '__main__':
    RogueLike()