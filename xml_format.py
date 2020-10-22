import os
import re
import csv
import sys
from shanten import get_yuko

COUNT = float('inf')
MAX = 1000


def pai_transform(x):
    if x == 16:
        return 34
    if x == 52:
        return 35
    if x == 88:
        return 36
    return x // 4


def bit_sum(m):
    return sum([m[i] * (2 ** i) for i in range(len(m))])


def huro_transform(m):
    CHI = 2 * 3 * 21
    PON = 2 * 34
    b = []
    for i in range(0, 16):
        b.append(m % 2)
        m = m // 2

    who = b[0] + b[1] * 2

    if who == 0:
        # 暗槓
        return CHI + PON + bit_sum(b[8:16]) // 3

    else:
        # 順子
        if b[2] == 1:
            ret = 0
            tmp = bit_sum(b[10:16])
            ret += tmp
            tmp = (tmp // 3) % 7
            # 赤あり
            if tmp == 2 and bit_sum(b[7:9]) == 0:
                ret += 63
            elif tmp == 3 and bit_sum(b[5:7]) == 0:
                ret += 63
            elif tmp == 4 and bit_sum(b[3:5]) == 0:
                ret += 63

            return ret

        # 明刻
        elif b[3] == 1:
            ret = CHI
            tmp = bit_sum(b[9:16]) // 3
            ret += tmp
            # 赤あり
            if tmp in [4, 13, 22] and bit_sum(b[5:7]) != 0:
                ret += 34
            return ret

        # 加槓
        elif b[4] == 1:
            return CHI + PON + 34 + bit_sum(b[9:16]) // 3

        # 明槓
        else:
            return CHI + PON + 68 + bit_sum(b[8:16]) // 4


count = 0


def xml_parse(filename):
    global count
    with open(filename, 'r') as xml:
        for elem, attr in re.findall(r'<(.*?)[ /](.*?)/?>', xml.read()):
            attr = dict(re.findall(r'\s?(.*?)="(.*?)"', attr))
            if elem == 'INIT':
                tsumo = [[] for _ in range(4)]
                x = [[] for _ in range(4)]

            # ツモ情報
            if re.match(r'[T|U|V|W][0-9]+', elem):
                idx = {'T': 0, 'U': 1, 'V': 2, 'W': 3}
                who = idx[elem[0]]
                pai = int(elem[1:])
                tsumo[who].append(pai)

            # 打牌情報
            if re.match(r'[D|E|F|G][0-9]+', elem):
                idx = {'D': 0, 'E': 1, 'F': 2, 'G': 3}
                who = idx[elem[0]]
                pai = int(elem[1:])
                # 手出し
                if len(tsumo[who]) != 0 and tsumo[who][-1] != pai:
                    x[who].append(pai_transform(pai))
                # ツモ切り
                else:
                    x[who].append(pai_transform(pai) + 37)

            # 副露情報
            if elem == 'N':
                who = int(attr['who'])
                x[who].append(74 + huro_transform(int(attr['m'])))

            # 和了情報
            if elem == 'AGARI':
                who = int(attr['who'])
                while len(x[who]) < 30:
                    x[who].append(MAX)

                doraHai = [pai_transform(int(i))
                           for i in attr['doraHai'].split(',')]
                if len(doraHai) > 4:
                    print(attr)
                    input()

                while len(doraHai) < 4:
                    doraHai.append(MAX)

                tehai = [0 for _ in range(34)]
                machi = int(attr['machi'])
                y = [0] * 34
                for i in map(int, attr['hai'].split(',')):
                    if i != machi:
                        tehai[i // 4] += 1

                for i in get_yuko(tehai, [4] * 34, 0):
                    y[i] = 1

                with open('sample.csv', 'a') as f:
                    writer = csv.writer(f)
                    writer.writerow(y + doraHai + x[who])
                    count += 1
                    if count >= COUNT:
                        sys.exit()


def xml_format(year, output_file_name='output.json'):
    file_dir = './xml' + str(year)
    for filename in os.listdir(file_dir):
        xml_parse(file_dir + '/' + filename)
        print(count, filename)


xml_format(2017)
