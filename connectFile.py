from itertools import chain
from collections import defaultdict
from heapq import heappush, heappop

import numpy


class FileConnector:
    PLAY_DATA_FILE = u"play_data.txt"
    GAME_EVALUATE_FILE = u"game_evaluate.txt"
    OUTPUT_FILE = u"output.txt"

    def __init__(self):
        self.play_data = []
        with open(self.PLAY_DATA_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                self.play_data.append(list(map(int, line.split(','))))
        self.evaluate_data = []
        with open(self.GAME_EVALUATE_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                user, name, point = line.rstrip().split(',')
                self.evaluate_data.append([int(user), name, int(point)])

    def get_recommend(self, user_data):
        user_data = numpy.asarray(list(chain(*user_data)), dtype='float32')
        user_numbers = dict([(x[0], i) for i, x in enumerate(self.play_data)])
        other_data = numpy.asarray([x[1:] for x in self.play_data], dtype='float32')
        max_value = numpy.max(other_data, axis=0)
        max_value[max_value == 0] = 1
        other_data = other_data / max_value
        user_data = user_data / max_value
        similarity = 1 - numpy.sum(numpy.power(other_data - user_data, 2), axis=1) / len(user_data)

        total_point = defaultdict(float)
        user_num = defaultdict(int)
        for user, game, point in self.evaluate_data:
            total_point[game] += point*similarity[user_numbers[user]]
            user_num[game] += 1
        recommend = []
        for key, value in total_point.items():
            heappush(recommend, (-value/user_num[key], key))
        return recommend

    def insert_play_data(self, user_data, favorite_data):
        with open(self.OUTPUT_FILE, 'w') as f:
            f.write(' '.join(map(str, list(chain(*user_data)))))
            f.write('\n')
            for name, point in favorite_data:
                f.write("{} {}\n".format(name, point))