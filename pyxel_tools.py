import pyxel


def text_mc(x, y, text_list, color_list):
    '''
    複数の色で文字を描画する
    :param x: 描画位置
    :param y: 描画位置
    :param text_list: 表示する文字のリスト
    :param color_list: 対応するtext_listの文字の色のリスト
    :return:
    '''
    TEXT_W = 4
    for i, s in enumerate(text_list):
        pyxel.text(x, y, s, color_list[i])
        x += len(s) * TEXT_W


def center(text, width):
    '''
    文章を中央揃えで表示する際のx座標を返す
    :param text: 座標を得たい文章
    :param width: 画面の幅
    :return:
    '''
    TEXT_W = 4
    return width // 2 - len(text) * TEXT_W // 2


class ParticleSystem:
    particles = []

    @classmethod
    def update(cls):
        for p in ParticleSystem.particles:
            p.update()
        ParticleSystem.particles = [p for p in ParticleSystem.particles if p.time > 0]

    @classmethod
    def draw(cls):
        for p in ParticleSystem.particles:
            p.draw()

    @classmethod
    def generate(cls, x, y, u, v, w, h, time, flame=1, colkey=None):
        ParticleSystem.particles.append(ParticleSystem.Particle(x, y, u, v, w, h, time, flame, colkey))

    class Particle:
        def __init__(self, x, y, u, v, w, h, time, flame=1, colkey=None):
            self.x = x
            self.y = y
            self.u = u
            self.v = v
            self.w = w
            self.h = h
            self.max_time = time
            self.time = time
            self.flame = flame
            self.colkey = colkey

        def update(self):
            self.time -= 1

        def draw(self):
            current_flame = int((self.max_time - self.time)/self.max_time*self.flame)
            if self.colkey:
                pyxel.blt(self.x - self.w/2, self.y - self.h/2, 0, self.u + current_flame*self.w, self.v, self.w, self.h, self.colkey)
            else:
                pyxel.blt(self.x - self.w/2, self.y - self.h/2, 0, self.u + current_flame*self.w, self.v, self.w, self.h)
