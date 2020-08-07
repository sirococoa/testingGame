from random import random, randrange, randint
import numpy
from scipy import signal
from copy import copy

import pyxel

WINDOW_WIDTH = 256
WINDOW_HEIGHT = 256


class RogueLike:
    stage = None

    def __init__(self):
        pyxel.init(WINDOW_WIDTH, WINDOW_HEIGHT)
        pyxel.load('rogue.pyxres')
        RogueLike.stage = Stage(30, 30)
        self.player = Player()
        self.player.spawn()
        pyxel.run(self.update, self.draw)

    def update(self):
        self.player.update()

    def draw(self):
        RogueLike.stage.draw(self.player.x, self.player.y)
        self.player.draw()


def translate_tile_num(base, shift):
    return [base + shift, base + shift + 1, base + 32 + shift, base + 32 + shift +1]


class Stage:
    tile_num = list(map(translate_tile_num,
                    (0, 128, 128, 192, 256, 256, 256, 192, 128, 128, 192, 192, 128, 256, 256, 256, 128, 192, 256),
                    (0, 2,   4,   4,   4,   2,   0,   0,   0,   8,   8,   6,   6,   6,   8,   10,  12,  12,  12)))
    tile_kind = (
        (int("000000100", 2), 11),
        (int("100000000", 2), 12),
        (int("001000000", 2), 9),
        (int("000000001", 2), 10),
        (int("000000010", 2), 1),
        (int("000100000", 2), 3),
        (int("010000000", 2), 5),
        (int("000001000", 2), 7),
        (int("000100110", 2), 2),
        (int("110100000", 2), 4),
        (int("011001000", 2), 6),
        (int("000001011", 2), 8),
        (int("010000010", 2), 14),
        (int("000101000", 2), 17),
        (int("011001011", 2), 13),
        (int("110100110", 2), 15),
        (int("000101111", 2), 16),
        (int("111101000", 2), 18),
    )

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.filter = numpy.array([2 ** i for i in range(9)]).reshape((3, 3))
        self.make_stage()

    def make_stage(self):
        self.block = Block(self.width, self.height)
        for _ in range(Block.MAX_NUM):
            self.block.divide()
        self.block.make_room()
        self.block.make_path()

        self.data = numpy.zeros((self.width, self.height), dtype=int)

        # room の追加
        for x, y, room in self.block.rooms():
            for i in range(x + room.sx, x + room.sx + room.width):
                for j in range(y + room.sy, y + room.sy + room.height):
                    self.data[i, j] = 1

        # aisle の追加
        for s, t in self.block.paths():
            x1 = min(s[0], t[0])
            x2 = max(s[0], t[0])
            y1 = min(s[1], t[1])
            y2 = max(s[1], t[1])
            for i in range(x1, x2 + 1):
                for j in range(y1, y2 + 1):
                    self.data[i, j] = 1

        self.make_map()
        for i in range(self.width):
            for j in range(self.height):
                t1, t2, t3, t4 = Stage.tile_num[self.tile[i][j]]
                pyxel.tilemap(0).set(j * 2, i * 2, t1)
                pyxel.tilemap(0).set(j * 2 + 1, i * 2, t2)
                pyxel.tilemap(0).set(j * 2, i * 2 + 1, t3)
                pyxel.tilemap(0).set(j * 2 + 1, i * 2 + 1, t4)

        # for i in range(len(self.tile_num)):
        #     t1, t2, t3, t4 = Stage.tile_num[i]
        #     pyxel.tilemap(0).set(i, 0, t1)
        #     pyxel.tilemap(0).set(i, 1, t2)
        #     pyxel.tilemap(0).set(i, 2, t3)
        #     pyxel.tilemap(0).set(i, 3, t4)

    def make_map(self):
        terrain = signal.correlate(self.data, self.filter, mode='same')
        self.tile = numpy.zeros((self.width, self.height), dtype=int)
        for key, value in Stage.tile_kind:
            self.tile[terrain & key == key] = value
        self.tile[self.data == 1] = 0

        self.tile = self.tile.tolist()

    def collision(self, x, y):
        if 0 <= x <= self.width and 0 <= x <= self.height:
            return not bool(self.data[y, x])
        return True

    def choice_room(self):
        tmp = self.block
        while tmp.child:
            tmp = tmp.child[0]
        return tmp.room

    def draw(self, px, py):
        u = px*2 - WINDOW_WIDTH // 16
        v = py*2 - WINDOW_HEIGHT // 16
        pyxel.bltm(0, 0, 0, u, v, WINDOW_WIDTH // 8, WINDOW_HEIGHT // 8)


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
            target = randrange(1)
            if self.child[target].divide():
                return True
            return self.child[1 - target].divide()
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
    MAX_SIZE = 10

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


class Player:
    INIT_HP = 3
    INIT_ATK = 1
    U = 16
    V = 0
    W = 16
    H = 16

    def __init__(self):
        self.x = 0
        self.y = 0
        self.hp = Player.INIT_HP
        self.atk = Player.INIT_ATK
        self.direct = 0

    def update(self):
        new_x = self.x
        new_y = self.y
        if pyxel.btn(pyxel.KEY_W):
            new_y -= 1
            self.direct = 0
        elif pyxel.btn(pyxel.KEY_D):
            new_x += 1
            self.direct = 1
        elif pyxel.btn(pyxel.KEY_S):
            new_y += 1
            self.direct = 2
        elif pyxel.btn(pyxel.KEY_A):
            new_x -= 1
            self.direct = 3
        else:
            pass
        if not RogueLike.stage.collision(new_x, new_y):
            self.x = new_x
            self.y = new_y

    def spawn(self):
        init_room = RogueLike.stage.choice_room()
        self.y = randint(init_room.sx, init_room.sx + init_room.width)
        self.x = randint(init_room.sy, init_room.sy + init_room.height)


    def draw(self):
        pyxel.blt(WINDOW_WIDTH//2, WINDOW_WIDTH//2, 0, Player.U + Player.W * self.direct, Player.V, Player.W, Player.H)


if __name__ == '__main__':
    RogueLike()
    # pyxel.init(WINDOW_WIDTH, WINDOW_HEIGHT)
    # pyxel.load('rogue.pyxres')
    #
    # # pyxel.run(self.update, self.draw)
    # s = Stage(30, 30)
    # s.make_stage()
    # for line in s.data:
    #     print("".join(map(lambda x: str(x%10) if x != 0 else " ", line)))
    # for line in s.tile:
    #     print("".join(map(lambda x: str(x%10) if x != 0 else " ", line)))
    # s.draw()
    # pyxel.show()
    print()