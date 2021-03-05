import csv
import re
import os
from random import randint


class XMLFormat():
    def __init__(self, years, output_file):
        self.count = 0
        self.output_file = output_file
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
            # self.huro_type[who][3] += 1

        else:
            # 順子
            if b[2] == 1:
                x = self.b(b[10:16]) // 3
                x += (x // 7) * 2
                for i in range(3):
                    self.huro[who][x + i] += 1
                    self.tehai[who][x + i] -= 1
                self.tehai[who][self.last_dahai] += 1
                # self.huro_type[who][0] += 1

            # 明刻
            elif b[2] == 0 and b[3] == 1:
                self.huro[who][self.b(b[9:16]) // 3] += 3
                self.tehai[who][self.b(b[9:16]) // 3] -= 3
                self.tehai[who][self.last_dahai] += 1
                # self.huro_type[who][1] += 1

            # 加槓
            elif b[2] == 0 and b[4] == 1:
                self.huro[who][self.b(b[9:16]) // 3] += 1
                # self.huro_type[who][2] += 1
                # self.huro_type[who][1] -= 1

            # 大明槓
            else:
                self.huro[who][self.b(b[8:16]) // 4] += 4
                self.tehai[who][self.b(b[8:16]) // 4] -= 4
                self.tehai[who][self.last_dahai] += 1
                # self.huro_type[who][2] += 1

    def output(self, who, y):
        with open(self.output_file, 'a') as f:
            writer = csv.writer(f)
            # out -> 34, in -> 87
            x = [y]
            x += self.tehai[who]
            for i in range(who, who + 4):
                i = i % 4
                x += self.dahai[i]
                x += self.huro[i]
            writer.writerow(x)

    def xml_parse(self, filename):
        with open(filename, 'r') as xml:
            for elem, attr in re.findall(r'<(.*?)[ /](.*?)/?>', xml.read()):
                attr = dict(re.findall(r'\s?(.*?)="(.*?)"', attr))

                # 開局
                if elem == 'INIT':
                    self.ts += 1
                    self.dahai = [[0] * 34 for _ in range(4)]
                    self.tehai = [[0] * 34 for _ in range(4)]
                    self.reach = [[0] * 34 for _ in range(4)]
                    self.huro = [[0] * 34 for _ in range(4)]
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

                # 打牌
                elif re.match(r'[D|E|F|G][0-9]+', elem):
                    idx = {'D': 0, 'E': 1, 'F': 2, 'G': 3}
                    who = idx[elem[0]]
                    pai = int(elem[1:])
                    if randint(1, 50) == 1:
                        self.output(who, self.pai(pai))
                        self.count += 1
                        if self.count == 2000000:
                            exit()
                    self.dahai[who][self.pai(pai)] += 1
                    self.tehai[who][self.pai(pai)] -= 1
                    self.last_dahai = self.pai(pai)

                elif elem == 'N':
                    who = int(attr['who'])
                    self.m(who, int(attr['m']))

                # リーチ成立
                elif elem == 'REACH' and attr['step'] == '2':
                    who = int(attr['who'])
                    self.reach[who][self.dahai[who][-1]] = 4

                # 和了
                elif elem == 'AGARI':
                    who = int(attr['who'])
                    self.who = who


XMLFormat(
    years=[2016, 2017],
    output_file='data.csv'
)
