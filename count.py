import re
import os
from shanten import get_machi


class XMLFormat():
    def __init__(self, years, count):
        self.count = 0
        self.ac = 0
        self.mc = 0
        self.dc = 0
        for year in years:
            file_dir = './xml' + str(year)
            for filename in os.listdir(file_dir):
                self.filename = filename
                self.ts = -1
                self.xml_parse(file_dir + '/' + filename)
                self.count += 1
                print()
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
            self.huro_type[who][3] += 1
            # print(self.url())
            # print('暗槓', self.jpns(self.huro[who]))
            # input()

        else:
            # 順子
            if b[2] == 1:
                x = self.b(b[10:16]) // 3
                x += (x // 7) * 2
                for i in range(3):
                    self.huro[who].append(x + i)
                self.huro_type[who][0] += 1
                # print(self.url())
                # print('順子', self.jpns(self.huro[who]))
                # input()

            # 明刻
            elif b[2] == 0 and b[3] == 1:
                for _ in range(3):
                    self.huro[who].append(self.b(b[9:16]) // 3)
                self.huro_type[who][1] += 1
                # print(self.url())
                # print(b)
                # print('明刻', self.jpns(self.huro[who]))
                # input()

            # 加槓
            elif b[2] == 0 and b[4] == 1:
                # 加槓なので足すのは一つだけ
                self.huro[who].append(self.b(b[9:16]) // 3)
                self.huro_type[who][2] += 1
                self.huro_type[who][1] -= 1
                # print(self.url())
                # print('加槓', self.jpns(self.huro[who]))
                # input()

            # 大明槓
            else:
                for _ in range(4):
                    self.huro[who].append(self.b(b[8:16]) // 4)
                self.huro_type[who][2] += 1
                # print(self.url())
                # print('大明槓', self.jpns(self.huro[who]))
                # input()

    def machi(self, attr):
        tehai = [0] * 34
        atari = int(attr['machi'])
        for pai in map(int, attr['hai'].split(',')):
            if pai != atari:
                tehai[self.pai(pai)] += 1

        machi = [0] * 34
        for pai in get_machi(jun=tehai, rest=[4] * 34, n_huro=sum(self.huro_type[self.who])):
            machi[pai] = 1

        return machi

    # 全員
    def n_pai_all(self):
        y = [0] * 34
        for who in range(4):
            for pai in self.dahai[who]:
                y[pai] += 1

        return y

    # リーチ者
    def n_dahai(self):
        y = [0] * 34
        for pai in self.dahai[self.who]:
            y[pai] += 1

        return y

    def n_huro(self):
        y = [0] * 34
        for pai in self.huro[self.who]:
            y[pai] += 1

        return y

    def n_mpsz(self):
        y = [0] * 4
        for pai in self.dahai[self.who]:
            y[pai // 9] += 1

        return y

    def n_mpsz_of_first_6pais(self):
        y = [0] * 4
        for pai in self.dahai[self.who][:6]:
            y[pai // 9] += 1

        return y

    def n_dist(self):
        y = [0] * 5
        for pai in self.dahai[self.who]:
            if pai >= 27:
                continue
            y[abs(pai % 9 - 4)] += 1

        return y

    def n_dist_of_first_6pais(self):
        y = [0] * 5
        for pai in self.dahai[self.who][6:]:
            if pai >= 27:
                continue
            y[abs(pai % 9 - 4)] += 1

        return y

    def is_suzi(self):
        y = [0] * 27
        for i in range(27):
            if i not in self.dahai:
                continue
            if 0 <= i - 3 < 27 and (i - 3) // 9 == i // 9:
                y[i] += 1
            if 0 <= i + 3 < 27 and (i + 3) // 9 == i // 9:
                y[i] += 1

        return y

    def xml_parse(self, filename):
        with open(filename, 'r') as xml:
            for elem, attr in re.findall(r'<(.*?)[ /](.*?)/?>', xml.read()):
                attr = dict(re.findall(r'\s?(.*?)="(.*?)"', attr))

                # 開局
                if elem == 'INIT':
                    self.ts += 1
                    self.dahai = [[] for _ in range(4)]
                    self.reachpai = [[0] * 34 for _ in range(4)]
                    self.huro = [[] for _ in range(4)]
                    self.huro_type = [[0] * 4 for _ in range(4)]

                # 打牌
                elif re.match(r'[D|E|F|G][0-9]+', elem):
                    idx = {'D': 0, 'E': 1, 'F': 2, 'G': 3}
                    who = idx[elem[0]]
                    pai = int(elem[1:])
                    self.dahai[who].append(self.pai(pai))

                elif elem == 'N':
                    who = int(attr['who'])
                    self.m(who, int(attr['m']))

                # リーチ成立
                elif elem == 'REACH' and attr['step'] == '2':
                    who = int(attr['who'])
                    self.reachpai[who][self.dahai[who][-1]] = 1

                # 和了
                elif elem == 'AGARI':
                    who = int(attr['who'])
                    self.who = who
                    machi = self.machi(attr)
                    # for i in range(34):
                    #     if machi[i] and i in self.dahai[who]:
                    #         break
                    # else:
                    mc, dc = sum(machi), len(set(self.dahai[who]))
                    self.ac += 1
                    self.mc += mc
                    self.dc += dc
                    print(self.ac, self.mc, self.dc)
                    print(mc, dc)
                    # if mc >= 9:
                    #     print('待ちが5個より多い')
                    #     print(self.url())
                    #     input()


XMLFormat(
    years=[2016, 2017],
    count=float('inf')
)
