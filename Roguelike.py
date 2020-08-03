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

    def make_stage(self):
        pass

    def draw(self):
        pass


class Block:
    MIN_SIZE = 7
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.child = []
        self.split = 0    # 0:x, 1:y
        self.entrance = None
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
            w = randint(Room.MAX_SIZE, min(Room.MAX_SIZE, self.width - 2))
            h = randint(Room.MAX_SIZE, min(Room.MAX_SIZE, self.height - 2))
            sx = randint(1, self.width - w - 1)
            sy = randint(1, self.height - h - 1)
            self.room = Room(sx, sy, w, h)

    def make_entrance(self):
        if self.child:
            self.child[0].make_entrance()
            self.child[1].make_entrance()
            if self.split:
                self.entrance = [0 for _ in range(4)]
                self.entrance[0] = self.child[0].entrance[0]
                self.entrance[1] = self.child[0].entrance[1] + self.child[1].entrance[1]
                self.entrance[2] = self.child[1].entrance[2]
                self.entrance[3] = self.child[0].entrance[3] + self.child[1].entrance[3]
        else:
            self.entrance = [[self.room.generate_entrance(i)] for i in (1, 0, 1, 0)]      # 0:up, 1:right, 2:down, 3:left


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
            return randint(self.sy + 1, self.sy + self.height)
        else:
            return randint(self.sx + 1, self.sx + self.width)



if __name__ == '__main__':
    RogueLike()
    b = Block(100, 100)
    for _ in range(10):
        b.divide()
    print()