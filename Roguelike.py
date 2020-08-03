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


if __name__ == '__main__':
    RogueLike()
    b = Block(100, 100)
    for _ in range(10):
        b.divide()
    print()