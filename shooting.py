import pyxel

WINDOW_WIDTH = 80
WINDOW_HEIGHT = 160


class Shooting:
    def __init__(self):
        pyxel.init(WINDOW_WIDTH, WINDOW_HEIGHT)
        pyxel.run(self.update, self.draw)

    def update(self):
        pass

    def draw(self):
        pass

class Player:
    U = 1
    V = 4
    width = 14
    height = 12

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def update(self):
        pass

    def draw(self):
        pyxel.blt(self.x - Player.width//2, self.y - Player.height//2, 0, Player.U, Player.V, Player.width, Player.height, colkey=0)
