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
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def update(self):
        pass

    def draw(self):
        pass