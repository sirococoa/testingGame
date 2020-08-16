# -*- coding: utf8 -*-

import tkinter as tk
import subprocess
import functools


class RecommendSystem(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Game Recommend System")
        self.geometry("500x500")
        self.use_frame = GamePlayFrame(self)

    def switch_frame(self, new_frame_class):
        new_frame = new_frame_class(self)
        if self.use_frame is not None:
            self.use_frame.destroy()
        self.use_frame = new_frame


class GamePlayFrame(tk.Frame):
    GAME_NUM = 2
    GAME_LABEL = [u'shooting', u'rogue like']
    GAMES = [u'shooting', u'Roguelike']
    GAME_INFO = [
        """
        操作方法
        [A] or <- : 左に移動
        [D] or -> : 右に移動
        [Space]   : 弾を発射
        ルール
        隕石に衝突すると残機が1減り、0になった後、さらに隕石と衝突するとゲームオーバーです。
        一定時間生存したらクリアです。
        隕石を弾で撃ち落とすか、避けるかして生存を目指しましょう。
        """,
        """
        操作方法
        [W]     : 上に移動
        [S]     : 下に移動
        [A]     : 左に移動
        [D]     : 右に移動
        [Space] : 前方に攻撃
        ルール
        敵と戦いながら、ダンジョンを奥深く進んでいきましょう。
        ただし、深くなるほど敵は強くなり、数も増えていきます。
        道中落ちているアイテムを回収して自身を強化しましょう。
        剣を拾えば攻撃力が上がり、薬を拾えばHPが増加します。(さらに全回復!)
        """
    ]

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.widgets()
        self.play_flag = [False for _ in range(self.GAME_NUM)]
        self.play_data = [[] for _ in range(self.GAME_NUM)]
        self.select_game_num = 0

    def widgets(self):
        message = tk.Label(self, text=u'PLAY THESE GAME!')
        message.pack(side='top')

        button = []
        for i, name in enumerate(self.GAMES):
            tmp = tk.Button(self, text=name)
            tmp.bind('<Button-1>', functools.partial(self.select_game, number=i))
            button.append(tmp)
        for b in button:
            b.pack()

        self.game_info = tk.StringVar()
        self.game_info.set(self.GAME_INFO[0])
        game_info_message = tk.Label(self, textvariable=self.game_info)
        game_info_message.pack()

        next_button = tk.Button(self, text="Next")
        next_button.bind('<Button-1>', self.next)
        next_button.pack(side='bottom')

        play_button = tk.Button(self, text="Play")
        play_button.bind('<Button-1>', self.run_game)
        play_button.pack(anchor='se')

    def select_game(self, event, number):
        self.select_game_num = number
        self.game_info.set(self.GAME_INFO[number])

    def run_game(self, event):
        print('run ' + self.GAMES[self.select_game_num])
        cp = subprocess.run(['python', self.GAMES[self.select_game_num] + '.py'], encoding='utf-8', stdout=subprocess.PIPE)
        output = cp.stdout.rstrip('\n').split('\n')
        print('end ' + self.GAMES[self.select_game_num])
        if output:
            self.play_flag[self.select_game_num] = True
            self.play_data[self.select_game_num] = output

    def next(self, event):
        self.master.switch_frame(RecommendFrame)
        # if all(self.play_flag):
        #     self.master.switch_frame(RecommendFrame)
        # else:
        #     pass


class RecommendFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pack()
        self.widgets()

    def widgets(self):
        message = tk.Label(self, text=u'Recommend you game')
        message.pack(side='top')

        next_button = tk.Button(self, text="Next")
        next_button.bind('<Button-1>', self.next)
        next_button.pack(side='bottom')

    def next(self, event):
        self.master.switch_frame(RegisterFrame)


class RegisterFrame(tk.Frame):
    CHECK_BOX_NAME = ["好き", "少し好き", "少し嫌い", "嫌い"]
    EVALUATE_POINT = [2, 1, -1, -2]

    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pack()
        self.game_name_list = set()
        self.game_list = []
        self.evaluate = tk.IntVar()
        self.evaluate.set(0)
        self.info = tk.StringVar()
        self.widgets()

    def widgets(self):
        message = tk.Label(self, text=u'Write your favorite games!')
        message.pack(side='top')

        self.game_name_box = tk.Entry(self)
        self.game_name_box.pack()

        add_button = tk.Button(self, text="登録")
        add_button.bind('<Button-1>', self.add_favorite_game)
        add_button.pack()

        for i, name in enumerate(self.CHECK_BOX_NAME):
            radio_button = tk.Radiobutton(self, text=name, variable=self.evaluate, value=i)
            radio_button.pack()

        select_info = tk.Label(self, textvariable=self.info)
        select_info.pack()

    def add_favorite_game(self, event):
        name = self.game_name_box.get()
        if name and name not in self.game_name_list:
            self.game_name_list.add(name)
            self.game_list.append([name, self.evaluate.get()])
            self.info.set('\n'.join(map(lambda x: str(x[0]) + " " + self.CHECK_BOX_NAME[x[1]], self.game_list)))


if __name__ == '__main__':
    app = RecommendSystem()
    app.mainloop()