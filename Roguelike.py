from random import randrange, random, choice
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
        MAX_ROOM_SIZE = 12
        MIN_ROOM_SIZE = 7

        def __init__(self, x, y, w, h):
            self.x = x
            self.y = y
            self.w = w
            self.h = h

            self.coll = False

            self.enter = []

        def collision(self, other):
            if self == other:
                return False
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

        def grow(self, width, height):
            direct = randrange(0, 4)
            length = randrange(Stage.Aisle.MIN_LENGTH, Stage.Aisle.MAX_LENGTH)
            if direct == 0:
                ex = self.x
                ey = randrange(self.y + 1, self.y + self.h - 1)
                new_aisle = Stage.Aisle(ex, ey - 1, ex - length, ey + 1, direct, self)
            elif direct == 1:
                ex = self.x + self.w
                ey = randrange(self.y + 1, self.y + self.h - 1)
                new_aisle = Stage.Aisle(ex, ey - 1, ex + length, ey + 1, direct, self)
            elif direct == 2:
                ex = randrange(self.x + 1, self.x + self.w - 1)
                ey = self.y
                new_aisle = Stage.Aisle(ex - 1, ey, ex + 1, ey - length, direct, self)
            else:
                ex = randrange(self.x + 1, self.x + self.w - 1)
                ey = self.y + self.h
                new_aisle = Stage.Aisle(ex - 1, ey, ex + 1, ey + length, direct, self)

            if not new_aisle.enter_space(width, height):
                return False

            for other in chain(Stage.rooms, Stage.aisles):
                if new_aisle.collision(other):
                    return False

            if not new_aisle.grow(width, height):
                return False

            self.enter.append(new_aisle)
            Stage.aisles.append(new_aisle)

            return True

        def enter_space(self, width, height):
            if 0 <= self.x and self.x + self.w < width:
                if 0 <= self.y and self.y + self.h < height:
                    return True
            return False

        @classmethod
        def generate(cls, width, height, min_size, max_size):
            while True:
                x = randrange(0, width)
                y = randrange(0, height)
                w = randrange(min_size, max_size)
                h = randrange(min_size, max_size)
                if x + w <= width and y + h <= height:
                    break
            return Stage.Room(x, y, w, h)

    class Aisle:
        MAX_LENGTH = 4
        MIN_LENGTH = 2

        def __init__(self, x1, y1, x2, y2, direct, start):
            self.x1 = x1
            self.y1 = y1
            self.x2 = x2
            self.y2 = y2
            self.direct = direct
            self.x = min(self.x1, self.x2)
            self.y = min(self.y1, self.y2)
            self.w = abs(self.x1 - self.x2)
            self.h = abs(self.y1 - self.y2)
            self.start = start
            self.end = None

        def collision(self, other):
            if self == other or other == self.start:
                return False
            if type(other) is Stage.Room:
                if -self.w - 1 <= self.x - other.x <= other.w + 1:
                    if -self.h - 1 <= self.y - other.y <= other.h + 1:
                        return True
                return False
            else:
                if -self.w <= self.x - other.x <= other.w:
                    if -self.h <= self.y - other.y <= other.h:
                        return True
                return False

        def grow(self, width, height):
            if not self.end:
                rw = randrange(Stage.Room.MIN_ROOM_SIZE, Stage.Room.MAX_ROOM_SIZE)
                rh = randrange(Stage.Room.MIN_ROOM_SIZE, Stage.Room.MAX_ROOM_SIZE)
                if self.direct == 0:
                    new_room = Stage.Room(self.x2 - rw, self.y2, rw, rh)
                elif self.direct == 1:
                    new_room = Stage.Room(self.x2, self.y2, rw, rh)
                elif self.direct == 1:
                    new_room = Stage.Room(self.x2, self.y2 - rh, rw, rh)
                else:
                    new_room = Stage.Room(self.x2, self.y2, rw, rh)

                if not new_room.enter_space(width, height):
                    return False

                for other in chain(Stage.rooms, Stage.aisles):
                    if other != self and new_room.collision(other):
                        return False
                self.end = new_room
                Stage.rooms.append(new_room)
                return True

        def enter_space(self, width, height):
            if 0 <= self.x and self.x + self.w < width:
                if 0 <= self.y and self.y + self.h < height:
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
        Stage.rooms.append(Stage.Room.generate(self.width, self.height, Stage.Room.MIN_ROOM_SIZE, Stage.Room.MAX_ROOM_SIZE))
        for _ in range(self.max_room_num):
            target = choice(Stage.rooms)
            target.grow(self.width, self.height)
        self.translate()

    def translate(self):
        self.map = [[" " for _ in range(self.height)] for _ in range(self.width)]
        for room in Stage.rooms:
            for i in range(room.x + 1, room.x + room.w):
                for j in range(room.y + 1, room.y + room.h):
                    self.map[i][j] = 1
        for aisle in Stage.aisles:
            if aisle.direct == 0 or aisle.direct == 1:
                for i in range(aisle.x, aisle.x + aisle.w + 1):
                    self.map[i][aisle.y] = 2
            else:
                for j in range(aisle.y, aisle.y + aisle.h + 1):
                    self.map[aisle.x][j] = 2

    def draw(self):
        pass


if __name__ == '__main__':
    RogueLike()
    s = Stage(30, 30, 100, 7, 12)
    for line in s.map:
        print("".join(map(str, line)))