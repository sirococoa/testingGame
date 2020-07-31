from random import randrange, random
from itertools import combinations, chain

import pyxel


class RogueLike:
    def __init__(self):
        pass

    def update(self):
        pass

    def draw(self):
        pass


class Stage:
    rooms = []
    aisles = []

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

            self.enter = []

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

        def grow_aisle(self):
            direct = randrange(0, 4)
            length = randrange(Stage.Aisle.MIN_LENGTH, Stage.Aisle.MAX_LENGTH)
            if direct == 0:
                ex = self.x
                ey = randrange(self.y + 1, self.y + self.h - 1)
                new_aisle = Stage.Aisle(ex, ey, ex - length, ey)
            elif direct == 1:
                ex = self.x + self.w
                ey = randrange(self.y + 1, self.y + self.h - 1)
                new_aisle = Stage.Aisle(ex, ey, ex + length, ey)
            elif direct == 2:
                ex = randrange(self.x + 1, self.x + self.w - 1)
                ey = self.y
                new_aisle = Stage.Aisle(ex, ey, ex, ey - length)
            else:
                ex = randrange(self.x + 1, self.x + self.w - 1)
                ey = self.y + self.h
                new_aisle = Stage.Aisle(ex, ey, ex, ey + length)

            for other in chain(Stage.rooms, Stage.aisles):
                if new_aisle.collision(other):
                    break
            else:
                self.enter.append(new_aisle)
            return False

    class Aisle:
        MAX_LENGTH = 7
        MIN_LENGTH = 3

        def __init__(self, x1, y1, x2, y2):
            self.x1 = x1
            self.y1 = y1
            self.x2 = x2
            self.y2 = y2
            self.x = min(self.x1, self.x2)
            self.y = min(self.y1, self.y2)
            self.w = abs(self.x1 - self.x2)
            self.h = abs(self.y1 - self.y2)

        def collision(self, other):
            if -self.w <= self.x - other.x <= other.w:
                if -self.h <= self.y - other.y <= other.h:
                    return True
            return False

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
            if not a.coll and a.collision(b):
                b.coll = True
        self.room_list = [room for room in self.room_list if not room.coll]

        self.data = [[1 for _ in range(self.width)] for _ in range(self.height)]
        for room in self.room_list:
            for x in range(room.x + 1, room.x + room.w - 1):
                for y in range(room.y + 1, room.y + room.h - 1):
                    self.data[x][y] = 0

    def draw(self):
        pass


if __name__ == '__main__':
    RogueLike()