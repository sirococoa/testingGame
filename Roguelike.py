from random import random, randrange, randint

import pyxel


class RogueLike:
    def __init__(self):
        pass

    def update(self):
        pass

    def draw(self):
        pass


class Stage:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.make_stage()
        self.data = None

    def make_stage(self):
        block = Block(self.width, self.height)
        for _ in range(Block.MAX_NUM):
            block.divide()
        block.make_room()
        block.make_path()

        self.data = [[' ' for _ in range(self.height)] for _ in range(self.height)]

        # room の追加
        for x, y, room in block.rooms():
            for i in range(x + room.sx, x + room.sx + room.width):
                for j in range(y + room.sy, y + room.sy + room.height):
                    self.data[i][j] = 1

        # aisle の追加
        for s, t in block.paths():
            x1 = min(s[0], t[0])
            x2 = max(s[0], t[0])
            y1 = min(s[1], t[1])
            y2 = max(s[1], t[1])
            for i in range(x1, x2 + 1):
                for j in range(y1, y2 + 1):
                    self.data[i][j] = 2

    def draw(self):
        pass


class Block:
    MIN_SIZE = 10
    MAX_NUM = 8
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.child = []
        self.split = 0    # 0:左右に分割, 1:上下に分割
        self.path = None      # 0:up, 1:right, 2:down, 3:left
        self.room = None

    def divide(self):
        if self.child:
            return self.child[randrange(1)].divide()
        else:
            if random() < 0.5:
                if self.width <= Block.MIN_SIZE*2:
                    return False
                w = randint(Block.MIN_SIZE, self.width - Block.MIN_SIZE)
                self.child = [Block(w, self.height), Block(self.width - w, self.height)]
            else:
                if self.height <= Block.MIN_SIZE*2:
                    return False
                h = randint(Block.MIN_SIZE, self.height - Block.MIN_SIZE)
                self.child = [Block(self.width, h), Block(self.width, self.height - h)]
                self.split = 1
            return True

    def make_room(self):
        if self.child:
            self.child[0].make_room()
            self.child[1].make_room()
        else:
            w = randint(Room.MIN_SIZE, min(Room.MAX_SIZE, self.width - 3))
            h = randint(Room.MIN_SIZE, min(Room.MAX_SIZE, self.height - 3))
            sx = randint(2, self.width - w - 1)
            sy = randint(2, self.height - h - 1)
            self.room = Room(sx, sy, w, h)

    def make_path(self, x=0, y=0):
        if self.child:
            if self.split:
                self.child[0].make_path(x, y)
                self.child[1].make_path(x, y + self.child[0].height)

                self.path = [0 for _ in range(4)]
                self.path[0] = self.child[0].path[0]
                self.path[1] = self.child[0].path[1] + self.child[1].path[1]
                self.path[2] = self.child[1].path[2]
                self.path[3] = self.child[0].path[3] + self.child[1].path[3]
            else:
                self.child[0].make_path(x, y)
                self.child[1].make_path(x + self.child[0].width, y)

                self.path = [0 for _ in range(4)]
                self.path[0] = self.child[0].path[0] + self.child[1].path[0]
                self.path[1] = self.child[1].path[1]
                self.path[2] = self.child[0].path[2] + self.child[1].path[2]
                self.path[3] = self.child[0].path[3]
        else:
            self.path = [0 for _ in range(4)]
            self.path[0] = [Path(x + self.room.generate_entrance(0), self.room.sy - 1)]
            self.path[1] = [Path(y + self.room.generate_entrance(1), self.width - self.room.sx - self.room.width)]
            self.path[2] = [Path(x + self.room.generate_entrance(0), self.height - self.room.sy - self.room.height)]
            self.path[3] = [Path(y + self.room.generate_entrance(1), self.room.sx - 1)]

    def rooms(self, x=0, y=0):
        if self.child:
            if self.split:
                yield from self.child[0].rooms(x, y)
                yield from self.child[1].rooms(x, y + self.child[0].height)
            else:
                yield from self.child[0].rooms(x, y)
                yield from self.child[1].rooms(x + self.child[0].width, y)
        else:
            yield x, y, self.room

    def paths(self, x=0, y=0):
        if self.child:
            if self.split:
                positions = []
                for p in self.child[0].path[2]:
                    positions.append(p.pos)
                    yield (p.pos, y + self.child[0].height), (p.pos, y + self.child[0].height - p.length)
                for p in self.child[1].path[0]:
                    positions.append(p.pos)
                    yield (p.pos, y + self.child[0].height), (p.pos, y + self.child[0].height + p.length)
                yield (min(positions), y + self.child[0].height), (max(positions), y + self.child[0].height)
                yield from self.child[0].paths(x, y)
                yield from self.child[1].paths(x, y + self.child[0].height)
            else:
                positions = []
                for p in self.child[0].path[1]:
                    positions.append(p.pos)
                    yield (x + self.child[0].width, p.pos), (x + self.child[0].width - p.length, p.pos)
                for p in self.child[1].path[3]:
                    positions.append(p.pos)
                    yield (x + self.child[0].width, p.pos), (x + self.child[0].width + p.length, p.pos)
                yield (x + self.child[0].width, min(positions)), (x + self.child[0].width, max(positions))
                yield from self.child[0].paths(x, y)
                yield from self.child[1].paths(x + self.child[0].width, y)


class Room:
    MIN_SIZE = 5
    MAX_SIZE = 15

    def __init__(self, sx, sy, width, height):
        self.sx = sx
        self.sy = sy
        self.width = width
        self.height = height

    def generate_entrance(self, direct):
        if direct:
            return randint(self.sy + 1, self.sy + self.height - 1)
        else:
            return randint(self.sx + 1, self.sx + self.width - 1)


class Path:
    def __init__(self, pos, length):
        self.pos = pos
        self.length = length


if __name__ == '__main__':
    RogueLike()
    s = Stage(30, 30)
    s.make_stage()
    for line in s.data:
        print("".join(map(str, line)))
    print()