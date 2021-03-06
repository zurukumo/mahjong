import csv
import re
import os
from random import randint
from shanten import calc_shanten


class Format():
    DAHAI_MODE = 0
    RICHI_MODE = 1
    PON_MODE = 2
    CHI_MODE = 3
    KAN_MODE = 4

    SHUNTSU_TYPE = 0
    MINKO_TYPE = 1
    MINKAN_TYPE = 2
    ANKAN_TYPE = 3

    def __init__(self, years=[2015, 2016, 2017], mode=DAHAI_MODE, max_count=1500000):
        self.count = 0
        self.mode = mode
        self.max_count = max_count
        for year in years:
            file_dir = './xml' + str(year)
            for filename in os.listdir(file_dir):
                self.filename = filename
                self.ts = -1
                self.xml_parse(file_dir + '/' + filename)

    def url(self):
        return 'https://tenhou.net/0/?log={}&ts={}'.format(self.filename.replace('.xml', ''), self.ts)

    def jpnc(self, c):
        return ['1m', '2m', '3m', '4m', '5m', '6m', '7m', '8m', '9m',
                '1p', '2p', '3p', '4p', '5p', '6p', '7p', '8p', '9p',
                '1s', '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s',
                '東', '南', '西', '北', '白', '発', '中'][c]

    def jpns(self, s):
        return [self.jpnc(c) for c in s]

    def pai(self, x):
        return x // 4

    def b(self, m):
        return sum([m[i] * (2 ** i) for i in range(len(m))])

    def pon?():

    def m(self, who, m):
        b = []
        for _ in range(0, 16):
            b.append(m % 2)
            m = m // 2

        from_who = self.b(b[0:2])

        if from_who == 0:
            # 暗槓
            self.huro[who][self.b(b[8:16]) // 4] += 4
            self.tehai[who][self.b(b[8:16]) // 4] -= 4
            self.huro_type[who][Format.ANKAN_TYPE] += 1

        else:
            # 順子
            if b[2] == 1:
                x = self.b(b[10:16]) // 3
                x += (x // 7) * 2
                for i in range(3):
                    self.huro[who][x + i] += 1
                    self.tehai[who][x + i] -= 1
                self.tehai[who][self.last_dahai] += 1
                self.huro_type[who][Format.SHUNTSU_TYPE] += 1

            # 明刻
            elif b[2] == 0 and b[3] == 1:
                self.huro[who][self.b(b[9:16]) // 3] += 3
                self.tehai[who][self.b(b[9:16]) // 3] -= 3
                self.tehai[who][self.last_dahai] += 1
                self.huro_type[who][Format.MINKO_TYPE] += 1

            # 加槓
            elif b[2] == 0 and b[4] == 1:
                self.huro[who][self.b(b[9:16]) // 3] += 1
                self.huro_type[who][Format.MINKO_TYPE] -= 1
                self.huro_type[who][Format.MINKAN_TYPE] += 1

            # 大明槓
            else:
                self.huro[who][self.b(b[8:16]) // 4] += 4
                self.tehai[who][self.b(b[8:16]) // 4] -= 4
                self.tehai[who][self.last_dahai] += 1
                self.huro_type[who][Format.MINKAN_TYPE] += 1

    def output(self, who, y):
        # 出力ファイル名の決定
        if self.mode == Format.DAHAI_MODE:
            output_file = 'dahai.csv'
        elif self.mode == Format.RICHI_MODE:
            output_file = 'richi.csv'
        elif self.mode == Format.PON_MODE:
            output_file = 'pon.csv'
        elif self.mode == Format.CHI_MODE:
            output_file = 'chi.csv'
        elif self.mode == Format.KAN_MODE:
            output_file = 'kan.csv'

        with open(output_file, 'a') as f:
            writer = csv.writer(f)
            x = [y]
            x += self.tehai[who]
            for i in range(who, who + 4):
                i = i % 4
                x += self.dahai[i]
                x += self.huro[i]
            writer.writerow(x)

        self.count += 1
        print(self.count, '/', self.max_count)
        if self.count == self.max_count:
            print('終了')
            exit()

    def xml_parse(self, filename):
        with open(filename, 'r') as xml:
            actions = re.findall(r'<(.*?)[ /](.*?)/?>', xml.read())
            for action_i, (elem, attr) in enumerate(actions):
                attr = dict(re.findall(r'\s?(.*?)="(.*?)"', attr))

                # 開局
                if elem == 'INIT':
                    self.ts += 1
                    self.dahai = [[0] * 34 for _ in range(4)]
                    self.tehai = [[0] * 34 for _ in range(4)]
                    self.richi = [[0] * 34 for _ in range(4)]
                    self.huro = [[0] * 34 for _ in range(4)]
                    self.huro_type = [[0] * 4 for _ in range(4)]
                    self.last_dahai = -1

                    for player in range(4):
                        for p in map(int, attr['hai' + str(player)].split(',')):
                            self.tehai[player][self.pai(int(p))] += 1

                # ツモ
                elif re.match(r'[T|U|V|W][0-9]+', elem):
                    idx = {'T': 0, 'U': 1, 'V': 2, 'W': 3}
                    who = idx[elem[0]]
                    pai = int(elem[1:])
                    self.tehai[who][self.pai(pai)] += 1

                    # リーチ状況の抽出
                    if self.mode == Format.RICHI_MODE and sum(self.richi[who]) == 0:
                        n_huro = sum(self.huro_type[who])
                        n_ankan = self.huro_type[who][Format.ANKAN_TYPE]
                        if n_huro == n_ankan and calc_shanten(tehai=self.tehai[who], n_huro=n_ankan) == 0:
                            y = 1 if actions[action_i + 1][0] == 'REACH' else 0
                            self.output(who, y)

                # 打牌
                elif re.match(r'[D|E|F|G][0-9]+', elem):
                    idx = {'D': 0, 'E': 1, 'F': 2, 'G': 3}
                    who = idx[elem[0]]
                    pai = self.pai(int(elem[1:]))

                    # 打牌状況の抽出
                    if self.mode == Format.DAHAI_MODE and randint(1, 50) == 1:
                        self.output(who, pai)

                    # ポンの抽出
                    if self.mode == Format.PON_MODE:
                        for i in range(who + 1, who + 4):
                            i = i % 4
                            if self.tehai[i][pai] >= 2:

                    self.dahai[who][pai] += 1
                    self.tehai[who][pai] -= 1
                    self.last_dahai = pai

                # 副露
                elif elem == 'N':
                    who = int(attr['who'])
                    self.m(who, int(attr['m']))

                # リーチ成立
                elif elem == 'REACH' and attr['step'] == '2':
                    who = int(attr['who'])
                    self.richi[who][self.dahai[who][-1]] = 4

                # 和了
                elif elem == 'AGARI':
                    who = int(attr['who'])
                    self.who = who


Format(
    years=[2016, 2017],
    mode=Format.RICHI_MODE
)
