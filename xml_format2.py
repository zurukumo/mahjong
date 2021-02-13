import csv
import re
import os
from random import randint


class XMLFormat():
    def __init__(self, years, output, count):
        self.count = 0
        self.output = output
        for year in years:
            file_dir = './xml' + str(year)
            for filename in os.listdir(file_dir):
                self.filename = filename
                self.ts = -1
                self.xml_parse(file_dir + '/' + filename)
                self.count += 1
                print(self.count, filename)
                if self.count == count:
                    return

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
            for _ in range(4):
                self.huro[who].append(self.b(b[8:16]) // 4)
            # self.huro_type[who][3] += 1

        else:
            # 順子
            if b[2] == 1:
                x = self.b(b[10:16]) // 3
                x += (x // 7) * 2
                for i in range(3):
                    self.huro[who].append(x + i)
                # self.huro_type[who][0] += 1

            # 明刻
            elif b[2] == 0 and b[3] == 1:
                for _ in range(3):
                    self.huro[who].append(self.b(b[9:16]) // 3)
                # self.huro_type[who][1] += 1

            # 加槓
            elif b[2] == 0 and b[4] == 1:
                self.huro[who].append(self.b(b[9:16]) // 3)
                # self.huro_type[who][2] += 1
                # self.huro_type[who][1] -= 1

            # 大明槓
            else:
                for _ in range(4):
                    self.huro[who].append(self.b(b[8:16]) // 4)
                # self.huro_type[who][2] += 1

    def xml_parse(self, filename):
        with open(filename, 'r') as xml:
            for elem, attr in re.findall(r'<(.*?)[ /](.*?)/?>', xml.read()):
                attr = dict(re.findall(r'\s?(.*?)="(.*?)"', attr))

                # 開局
                if elem == 'INIT':
                    self.ts += 1
                    self.dahai = [[0] * 34 for _ in range(4)]
                    self.reach = [[0] * 34 for _ in range(4)]
                    self.huro = [[0] * 34 for _ in range(4)]

                # 打牌
                elif re.match(r'[D|E|F|G][0-9]+', elem):
                    idx = {'D': 0, 'E': 1, 'F': 2, 'G': 3}
                    who = idx[elem[0]]
                    pai = int(elem[1:])
                    self.dahai[who][self.pai(pai)] += 1

                elif elem == 'N':
                    who = int(attr['who'])
                    print(self.m(who, int(attr['m'])))

                # リーチ成立
                elif elem == 'REACH' and attr['step'] == '2':
                    who = int(attr['who'])
                    self.reach[who][self.dahai[who][-1]] = 1

                # 和了
                elif elem == 'AGARI':
                    who = int(attr['who'])
                    self.who = who
                    # with open(self.output, 'a') as f:
                    #     writer = csv.writer(f)
                    #     # out -> 34, in -> 87
                    #     writer.writerow(
                    #         self.machi(attr) +  # 34
                    #         self.n_pai_all() +  # 34
                    #         self.n_dahai() +  # 34
                    #         self.n_huro() +  # 34
                    #         self.n_mpsz() +  # 4
                    #         self.n_mpsz_of_first_6pais() +  # 4
                    #         self.n_dist() +  # 5
                    #         self.n_dist_of_first_6pais() +  # 5
                    #         self.is_suzi() +  # 27
                    #         self.reach[who] +   # 34
                    #         self.huro_type[who]  # 34
                    #     )


XMLFormat(
    years=[2016, 2017],
    output='data2.csv',
    count=float('inf')
)
