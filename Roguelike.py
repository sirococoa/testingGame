from random import random, randrange, randint
import numpy
from scipy import signal
from copy import copy

import pyxel

import pyxel_tools as pt
from astar import a_star

WINDOW_WIDTH = 256
WINDOW_HEIGHT = 256


class RogueLike:
    stage = None
    enemy_list =[]

    def __init__(self):
        pyxel.init(WINDOW_WIDTH, WINDOW_HEIGHT)
        pyxel.load('rogue.pyxres')
        self.state = 0 # 0:player -> 1 -> 2:enemy -> 3 -> 0
        RogueLike.stage = Stage(30, 30)
        self.player = Player()
        self.player.spawn()
        RogueLike.enemy_list.append(Enemy(10, 10))
        RogueLike.enemy_list.append(Enemy(10, 10))
        RogueLike.enemy_list.append(Enemy(10, 10))
        pyxel.run(self.update, self.draw)

    def update(self):
        if self.state == 0:
            if self.player.update():
                self.state += 1
            if self.player.on_stair():
                RogueLike.stage.make_stage()
                self.player.spawn()
        if self.state == 1:
            if pt.ParticleSystem.particles:
                pt.ParticleSystem.update()
                return
            self.state += 1
        if self.state == 2:
            Enemy.load_stage_data()
            for enemy in RogueLike.enemy_list:
                enemy.update(self.player.x, self.player.y)
            self.state += 1
        if self.state == 3:
            if pt.ParticleSystem.particles:
                pt.ParticleSystem.update()
                return
            self.state = 0

        RogueLike.enemy_list = [enemy for enemy in RogueLike.enemy_list if enemy.hp > 0]


    def draw(self):
        pyxel.cls(0)
        RogueLike.stage.draw(self.player.x, self.player.y)
        self.player.draw()
        for enemy in RogueLike.enemy_list:
            enemy.draw(self.player.x, self.player.y)
        pt.ParticleSystem.draw()


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
    stair_x = 0
    stair_y = 0
    stair_u = 0
    stair_v = 80

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.filter = numpy.array([2 ** i for i in range(9)]).reshape((3, 3))
        self.make_stage()

    def make_stage(self):
        self.block = Block(0, 0, self.width, self.height)
        for _ in range(Block.MAX_NUM):
            self.block.divide()
        self.block.make_room()
        self.block.make_path()

        self.data = numpy.zeros((self.width, self.height), dtype=int)

        # room の追加
        for room in self.block.rooms():
            for i in range(room.x, room.x + room.width):
                for j in range(room.y, room.y + room.height):
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

        Stage.stair_x, Stage.stair_y = self.choice_room_point()

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
            tmp = tmp.child[randint(0, 1)]
        return tmp.room

    def choice_room_point(self):
        r = self.choice_room()
        return randint(r.y, r.y + r.height - 1), randint(r.x, r.x + r.width - 1)

    def draw(self, px, py):
        u = px*2 - WINDOW_WIDTH // 16
        v = py*2 - WINDOW_HEIGHT // 16
        pyxel.bltm(0, 0, 0, u, v, WINDOW_WIDTH // 8, WINDOW_HEIGHT // 8)

        sx = (Stage.stair_x - px) + WINDOW_WIDTH // 32
        sy = (Stage.stair_y - py) + WINDOW_HEIGHT // 32
        pyxel.blt(sx * 16, sy * 16, 0, Stage.stair_u, Stage.stair_v, 16, 16)


class Block:
    MIN_SIZE = 10
    MAX_NUM = 8
    
    def __init__(self,x, y, width, height):
        self.x = x
        self.y = y
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
                self.child = [Block(self.x, self.y, w, self.height), Block(self.x + w, self.y, self.width - w, self.height)]
            else:
                if self.height <= Block.MIN_SIZE*2:
                    return False
                h = randint(Block.MIN_SIZE, self.height - Block.MIN_SIZE)
                self.child = [Block(self.x, self.y, self.width, h), Block(self.x, self.y + h, self.width, self.height - h)]
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
            self.room = Room(self.x + sx, self.y + sy, w, h, sx, sy)

    def make_path(self):
        self.path = [0 for _ in range(4)]
        if self.child:
            self.child[0].make_path()
            self.child[1].make_path()
            if self.split:
                self.path[0] = self.child[0].path[0]
                self.path[1] = self.child[0].path[1] + self.child[1].path[1]
                self.path[2] = self.child[1].path[2]
                self.path[3] = self.child[0].path[3] + self.child[1].path[3]
            else:
                self.path[0] = self.child[0].path[0] + self.child[1].path[0]
                self.path[1] = self.child[1].path[1]
                self.path[2] = self.child[0].path[2] + self.child[1].path[2]
                self.path[3] = self.child[0].path[3]
        else:
            self.path[0] = [Path(self.room.generate_entrance(0), self.room.sy - 1)]
            self.path[1] = [Path(self.room.generate_entrance(1), self.width - self.room.sx - self.room.width)]
            self.path[2] = [Path(self.room.generate_entrance(0), self.height - self.room.sy - self.room.height)]
            self.path[3] = [Path(self.room.generate_entrance(1), self.room.sx - 1)]

    def rooms(self):
        if self.child:
            yield from self.child[0].rooms()
            yield from self.child[1].rooms()
        else:
            yield self.room

    def paths(self):
        if self.child:
            if self.split:
                positions = []
                for p in self.child[0].path[2]:
                    positions.append(p.pos)
                    yield (p.pos, self.y + self.child[0].height), (p.pos, self.y + self.child[0].height - p.length)
                for p in self.child[1].path[0]:
                    positions.append(p.pos)
                    yield (p.pos, self.y + self.child[0].height), (p.pos, self.y + self.child[0].height + p.length)
                yield (min(positions), self.y + self.child[0].height), (max(positions), self.y + self.child[0].height)
                yield from self.child[0].paths()
                yield from self.child[1].paths()
            else:
                positions = []
                for p in self.child[0].path[1]:
                    positions.append(p.pos)
                    yield (self.x + self.child[0].width, p.pos), (self.x + self.child[0].width - p.length, p.pos)
                for p in self.child[1].path[3]:
                    positions.append(p.pos)
                    yield (self.x + self.child[0].width, p.pos), (self.x + self.child[0].width + p.length, p.pos)
                yield (self.x + self.child[0].width, min(positions)), (self.x + self.child[0].width, max(positions))
                yield from self.child[0].paths()
                yield from self.child[1].paths()


class Room:
    MIN_SIZE = 5
    MAX_SIZE = 10

    def __init__(self, x, y, width, height, sx, sy):
        self.x = x
        self.y = y
        self.sx = sx
        self.sy = sy
        self.width = width
        self.height = height

    def generate_entrance(self, direct):
        if direct:
            return randint(self.y + 1, self.y + self.height - 1)
        else:
            return randint(self.x + 1, self.x + self.width - 1)


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
    ATK_TARGET = ((0, -1), (1, 0), (0, 1), (-1, 0))

    def __init__(self):
        self.x = 0
        self.y = 0
        self.hp = Player.INIT_HP
        self.atk = Player.INIT_ATK
        self.direct = 0

    def update(self):
        if pyxel.btn(pyxel.KEY_SPACE):
            atk_x = self.x + Player.ATK_TARGET[self.direct][0]
            atk_y = self.y + Player.ATK_TARGET[self.direct][1]
            for enemy in RogueLike.enemy_list:
                if atk_x == enemy.x and atk_y == enemy.y:
                    enemy.hp -= self.atk
                    break
            AtkEffect.generate(atk_x, atk_y, self.x, self.y)
            return True

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
            return False

        for enemy in RogueLike.enemy_list:
            if new_x == enemy.x and new_y == enemy.y:
                return False

        if not RogueLike.stage.collision(new_x, new_y):
            self.x = new_x
            self.y = new_y
            return True
        return False

    def spawn(self):
        self.x, self.y = RogueLike.stage.choice_room_point()

    def on_stair(self):
        return self.x == Stage.stair_x and self.y == Stage.stair_y

    def draw(self):
        pyxel.blt(WINDOW_WIDTH//2, WINDOW_WIDTH//2, 0, Player.U + Player.W * self.direct, Player.V, Player.W, Player.H)


class Enemy:
    U = 80
    V = 0
    W = 16
    H = 16
    stage_data = None

    def __init__(self, hp, atk):
        self.hp = hp
        self.atk = atk
        self.direct = 0
        self.spawn()

    def spawn(self):
        self.x, self.y = RogueLike.stage.choice_room_point()

    def update(self, px, py):
        d, route = a_star(Enemy.stage_data, (self.x, self.y), (px, py))

        if route is None:
            print()

        tmp = route[(px, py)]
        new_x = px
        new_y = py
        while tmp != (self.x, self.y):
            new_x = tmp[0]
            new_y = tmp[1]
            tmp = route[tmp]

        if self.x - new_x == 1:
            self.direct = 3
        if self.x - new_x == -1:
            self.direct = 1
        if self.y - new_y == 1:
            self.direct = 0
        if self.y - new_y == -1:
            self.direct = 2

        if (new_x, new_y) == (px, py):
            AtkEffect.generate(px, py, px, py)
            return

        for enemy in RogueLike.enemy_list:
            if enemy != self:
                if enemy.x == new_x and enemy.y == new_y:
                    return

        if not RogueLike.stage.collision(new_x, new_y):
            self.x = new_x
            self.y = new_y

    def draw(self, px, py):
        draw_x = (self.x - px) + WINDOW_WIDTH // 32
        draw_y = (self.y - py) + WINDOW_HEIGHT // 32
        pyxel.blt(draw_x * 16, draw_y * 16, 0, Enemy.U + Enemy.W * self.direct, Enemy.V, Enemy.W, Enemy.H)

    @classmethod
    def load_stage_data(cls):
        Enemy.stage_data = RogueLike.stage.data.T.tolist()
        for enemy in RogueLike.enemy_list:
            Enemy.stage_data[enemy.x][enemy.y] = 4


class AtkEffect:
    U = 0
    V = 16
    W = 16
    H = 16
    TIME = 10
    FLAME = 1

    @classmethod
    def generate(cls, x, y, px, py):
        draw_x = (x - px) + WINDOW_WIDTH // 32
        draw_y = (y - py) + WINDOW_HEIGHT // 32
        pt.ParticleSystem.generate(draw_x * 16 + 8, draw_y * 16 + 8, AtkEffect.U, AtkEffect.V, AtkEffect.W, AtkEffect.H, AtkEffect.TIME, AtkEffect.FLAME, colkey=0)


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