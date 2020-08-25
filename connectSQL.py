from itertools import chain
from collections import defaultdict
from heapq import heappush, heappop

import numpy
import mysql.connector as mydb


class MysqlConnector:
    def __init__(self, ip):
        self.conn = mydb.connect(
            host=ip,
            port='3306',
            user='player',
            password='AS24dg',
            database='testingGame'
        )
        self.conn.ping(reconnect=True)
        print(self.conn.is_connected())

    def get_recommend(self, play_data):
        play_data = numpy.asarray(list(chain(*play_data)), dtype='float32')
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM play_data")
        data = cur.fetchall()
        user_numbers = dict([(x[0], i) for i, x in enumerate(data)])
        other_data = numpy.asarray([x[1:] for x in data], dtype='float32')
        max_value = numpy.max(other_data, axis=0)
        max_value[max_value == 0] = 1
        other_data = other_data / max_value
        play_data = play_data / max_value
        similarity = 1 - numpy.sum(numpy.power(other_data - play_data, 2), axis=1) / len(play_data)

        cur.execute("SELECT * FROM game_evaluate")
        other_favorite = cur.fetchall()

        total_point = defaultdict(float)
        user_num = defaultdict(int)
        for user, game, point in other_favorite:
            total_point[game] += point*similarity[user_numbers[user]]
            user_num[game] += 1
        recommend = []
        for key, value in total_point.items():
            heappush(recommend, (-value/user_num[key], key))
        return recommend

    def insert_play_data(self, play_data, favorite_data):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO play_data VALUES (0, " + ", ".join(map(str, chain(*play_data))) + ")")
        cur.executemany("INSERT INTO game_evaluate VALUES (LAST_INSERT_ID(), %s, %s)", favorite_data)
        cur.close()
        self.conn.commit()

    def end(self):
        self.conn.close()

    def connect(self):
        return self.conn.is_connected()


if __name__ == '__main__':
    db = MysqlConnector()
    play_data = [list(range(6)), list(range(8))]
    favorite_data = [["Minecraft", 2], ["Fortnite", -1]]
    # db.insert_play_data(play_data, favorite_data)
    r = db.get_recommend(play_data)
    # db.end()
    print()