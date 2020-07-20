from random import randint, random

import pyxel
import pyxel_tools as pt

WINDOW_WIDTH = 80
WINDOW_HEIGHT = 160


class Shooting:
    bullets = []
    asteroids = []
    MAX_ASTEROIDS_NUM = 10
    INIT_ASTEROIDS_RATE = 0.1

    def __init__(self):
        pyxel.init(WINDOW_WIDTH, WINDOW_HEIGHT)
        pyxel.load('shooting.pyxres')
        self.player = Player(WINDOW_WIDTH//2, int(WINDOW_HEIGHT*0.8))
        self.asteroid_rate = Shooting.INIT_ASTEROIDS_RATE
        self.gameover = None
        pyxel.run(self.update, self.draw)

    def update(self):
        if self.player.hp >= 0:
            self.player.update()
            for bullet in Shooting.bullets:
                bullet.update()
            Shooting.bullets = [bullet for bullet in Shooting.bullets if bullet.active]
            for asteroid in Shooting.asteroids:
                asteroid.update()
            Shooting.asteroids = [asteroid for asteroid in Shooting.asteroids if asteroid.active]
            if len(Shooting.asteroids) < Shooting.MAX_ASTEROIDS_NUM:
                if random() < self.asteroid_rate:
                    Shooting.asteroids.append(Asteroid.generate())
            if self.player.hp < 0:
                self.gameover = GameOver(0, False)
        else:
            self.gameover.update()

    def draw(self):
        pyxel.cls(0)
        if self.player.hp >= 0:
            self.player.draw()
            for bullet in Shooting.bullets:
                bullet.draw()
            for asteroid in Shooting.asteroids:
                asteroid.draw()
        else:
            self.gameover.draw()


class Player:
    U = 1
    V = 4
    width = 14
    height = 12
    speed = 2
    rate = 5
    INIT_HP = 3

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.cool_time = 0
        self.hp = Player.INIT_HP

    def update(self):
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A):
            self.x = max(0 + Player.width//2, self.x - Player.speed)
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_D):
            self.x = min(WINDOW_WIDTH - Player.width//2, self.x + Player.speed)
        if self.cool_time:
            self.cool_time -= 1
        else:
            if pyxel.btn(pyxel.KEY_SPACE):
                Shooting.bullets.append(Bullet(self.x, self.y))
                self.cool_time = Player.rate

        for asteroid in Shooting.asteroids:
            if abs(self.x - asteroid.x) <= Player.width//2 + Asteroid.width//2 and abs(self.y - asteroid.y) <= Player.height//2 + Asteroid.height//2:
                asteroid.active = False
                self.hp -= 1

    def draw(self):
        pyxel.blt(self.x - Player.width//2, self.y - Player.height//2, 0, Player.U, Player.V, Player.width, Player.height, colkey=0)


class Bullet:
    U = 22
    V = 3
    width = 4
    height = 10
    speed = 4

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.active = True

    def update(self):
        self.y -= Bullet.speed
        if self.y < -Bullet.height:
            self.active = False
        for asteroid in Shooting.asteroids:
            if abs(self.x - asteroid.x) <= Bullet.width//2 + Asteroid.width//2 and abs(self.y - asteroid.y) <= Bullet.height//2 + Asteroid.height//2:
                asteroid.active = False
                self.active = False
                return

    def draw(self):
        pyxel.blt(self.x - Bullet.width//2, self.y - Bullet.height//2, 0, Bullet.U, Bullet.V, Bullet.width, Bullet.height, colkey=0)


class Asteroid:
    U = 35
    V = 3
    width = 10
    height = 10
    speed_range = [1, 3]

    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.active = True

    def update(self):
        self.y += self.speed
        if self.y > WINDOW_HEIGHT + Asteroid.height:
            self.active = False

    def draw(self):
        pyxel.blt(self.x - Asteroid.width//2, self.y - Asteroid.height//2, 0, Asteroid.U, Asteroid.V, Asteroid.width, Asteroid.height, colkey=0)

    @classmethod
    def generate(cls):
        x = randint(Asteroid.width//2, WINDOW_WIDTH - Asteroid.width//2)
        y = -Asteroid.height
        speed = randint(*Asteroid.speed_range)
        return Asteroid(x, y, speed)


class GameOver:
    def __init__(self, score, clear=False):
        self.score = score
        self.clear = clear

    def update(self):
        pass

    def draw(self):
        if self.clear:
            message = "Game Clear"
        else:
            message = "Game Over"
        pyxel.text(pt.center(message, WINDOW_WIDTH), WINDOW_HEIGHT//2, message, 7)

        message = "Your Score : {}".format(str(self.score))
        pyxel.text(pt.center(message, WINDOW_WIDTH), WINDOW_HEIGHT//4*3, message, 7)


def draw_stock(num):
    stock_height = int(WINDOW_HEIGHT*0.9)
    u = 5
    v = 21
    w = 6
    h = 6
    interval = 2
    for i in range(num):
        pyxel.blt(i*(w + interval) + interval, stock_height, 0, u, v, w, h, colkey=0)


if __name__ == '__main__':
    Shooting()