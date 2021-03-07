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

    def __init__(self, years=[2015, 2016, 2017], mode=DAHAI_MODE, max_count=1500000, debug=False):
        self.count = 0
        self.mode = mode
        self.max_count = max_count
        self.debug = debug
        for year in years:
            file_dir = './xml' + str(year)
            for filename in os.listdir(file_dir):
                self.filename = filename
                self.ts = -1
                self.xml_parse(file_dir + '/' + filename)

    def url(self):
        return 'https://tenhou.net/0/?log={}&ts={}'.format(self.filename.replace('.xml', ''), self.ts)

    def jp(self, c):
        return ['1m', '2m', '3m', '4m', '5m', '6m', '7m', '8m', '9m',
                '1p', '2p', '3p', '4p', '5p', '6p', '7p', '8p', '9p',
                '1s', '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s',
                '東', '南', '西', '北', '白', '発', '中', '-'][c]

    def pai(self, x):
        return x // 4

    def is_ankan(self, m):
        return not bool(m & 0x0003)

    def is_shuntsu(self, m):
        return bool(m & 0x0004)

    def is_minko(self, m):
        return not self.is_shuntsu(m) and bool(m & 0x0008)

    def is_kakan(self, m):
        return not self.is_shuntsu(m) and bool(m & 0x0010)

    def is_minkan(self, m):
        return not (self.is_ankan(m) or self.is_shuntsu(m) or self.is_minko(m) or self.is_kakan(m))

    def is_kan(self, m):
        return self.is_ankan(m) or self.is_kakan(m) or self.is_minkan(m)

    def sample_richi(self, who):
        elem, _ = self.actions[self.action_i + 1]
        # リーチ中
        if sum(self.richi[who]) >= 1:
            return
        # 暗槓以外の副露をしている
        n_huro = sum(self.huro_type[who])
        n_ankan = self.huro_type[who][Format.ANKAN_TYPE]
        if n_huro != n_ankan:
            return

        if calc_shanten(tehai=self.tehai[who], n_huro=n_ankan) == 0:
            if elem == 'REACH':
                y = 1
            else:
                # ダマテンは継続しがちなので適宜飛ばす
                if randint(1, 3) <= 2:
                    return
                y = 0
            self.output(who, y)

    def sample_pon(self, pai, who):
        elem, attr = self.actions[self.action_i + 1]
        attr = dict(re.findall(r'\s?(.*?)="(.*?)"', attr))
        for i in range(who + 1, who + 4):
            i = i % 4
            # リーチ中
            if sum(self.richi[i]) >= 1:
                return
            # 次がロン
            if elem == 'AGARI' and attr['who'] != attr['fromWho']:
                return

            if self.tehai[i][pai] >= 2:
                if elem == 'N' and self.is_minko(int(attr['m'])):
                    y = 1
                else:
                    y = 0
                self.output(i, y)

    def sample_chi(self, pai, who):
        elem, attr = self.actions[self.action_i + 1]
        attr = dict(re.findall(r'\s?(.*?)="(.*?)"', attr))
        i = (who + 1) % 4
        # 字牌 or リーチ中
        if pai >= 27 or sum(self.richi[i]) >= 1:
            return
        # 次がロン
        if elem == 'AGARI' and attr['who'] != attr['fromWho']:
            return
        # 次がポン・カン
        if elem == 'N' and (self.is_minko(int(attr['m'])) or self.is_kan(int(attr['m']))):
            return

        cond1 = pai % 9 <= 6 and self.tehai[i][pai + 1] >= 1 and self.tehai[i][pai + 2] >= 1
        cond2 = 1 <= pai % 9 <= 7 and self.tehai[i][pai - 1] >= 1 and self.tehai[i][pai + 1] >= 1
        cond3 = 2 <= pai % 9 and self.tehai[i][pai - 2] >= 1 and self.tehai[i][pai - 1] >= 1
        if cond1 or cond2 or cond3:
            if elem == 'N' and self.is_shuntsu(int(attr['m'])):
                y = ((int(attr['m']) & 0xFC00) >> 10) % 3 + 1
            else:
                y = 0
            self.output(i, y)

    def m(self, who, m):
        if self.is_ankan(m):
            # 暗槓
            p = ((m & 0xFF00) >> 8) // 4
            self.huro[who][p] += 4
            self.tehai[who][p] -= 4
            self.huro_type[who][Format.ANKAN_TYPE] += 1
            # print(self.url())
            # print('暗槓', self.jp(p))
            # print('最後の打牌', self.jp(self.last_dahai))
            # input()

        else:
            # 順子
            if self.is_shuntsu(m):
                p = ((m & 0xFC00) >> 10) // 3
                p += (p // 7) * 2
                for i in range(3):
                    self.huro[who][p + i] += 1
                    self.tehai[who][p + i] -= 1
                self.tehai[who][self.last_dahai] += 1
                self.huro_type[who][Format.SHUNTSU_TYPE] += 1
                # print(self.url())
                # print('順子', self.jp(p))
                # t = ((m & 0xFC00) >> 10) % 3
                # print('鳴いた場所', t)
                # print('最後の打牌', self.jp(self.last_dahai))
                # input()

            # 明刻
            elif self.is_minko(m):
                p = ((m & 0xFE00) >> 9) // 3
                self.huro[who][p] += 3
                self.tehai[who][p] -= 3
                self.tehai[who][self.last_dahai] += 1
                self.huro_type[who][Format.MINKO_TYPE] += 1
                # print(self.url())
                # print('明刻', self.jp(p))
                # print('最後の打牌', self.jp(self.last_dahai))
                # input()

            # 加槓
            elif self.is_kakan(m) == 1:
                p = ((m & 0xFE00) >> 9) // 3
                self.huro[who][p] += 1
                self.huro_type[who][Format.MINKO_TYPE] -= 1
                self.huro_type[who][Format.MINKAN_TYPE] += 1
                # print(self.url())
                # print('加槓', self.jp(p))
                # input()

            # 大明槓
            else:
                p = ((m & 0xFF00) >> 8) // 4
                self.huro[who][p] += 4
                self.tehai[who][p] -= 4
                self.tehai[who][self.last_dahai] += 1
                self.huro_type[who][Format.MINKAN_TYPE] += 1
                # print(self.url())
                # print('大明槓', self.jp(p))
                # print('最後の打牌', self.jp(self.last_dahai))
                # input()

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
            # 手牌(1)
            x += self.tehai[who]
            # 捨て牌(4)
            for i in range(who, who + 4):
                i = i % 4
                x += self.dahai[i]
            # 副露牌(4)
            for i in range(who, who + 4):
                i = i % 4
                x += self.huro[i]
            # 最後の打牌(1)
            x += [4 if i == self.last_dahai else 0 for i in range(34)]
            writer.writerow(x)

            # デバッグ開始
            if self.debug:
                print(self.url())
                debug = ''
                for i in range(34):
                    for _ in range(self.tehai[who][i]):
                        debug += self.jp(i)
                print('手牌:', debug)
                print()
                for n in range(who, who + 4):
                    n = n % 4
                    debug = ''
                    for i in range(34):
                        for _ in range(self.dahai[n][i]):
                            debug += self.jp(i)
                    print('捨て牌:', debug)
                print()
                for n in range(who, who + 4):
                    n = n % 4
                    debug = ''
                    for i in range(34):
                        for _ in range(self.huro[n][i]):
                            debug += self.jp(i)
                    print('副露:', debug)
                print()
                debug = ''
                debug += self.jp(self.last_dahai)
                print('最後の打牌:', debug)
                print('結果:', self.jp(y) if self.mode == Format.DAHAI_MODE else y)
                input()

        self.count += 1
        print(self.count, '/', self.max_count)
        if self.count == self.max_count:
            print('終了')
            exit()

    def xml_parse(self, filename):
        with open(filename, 'r') as xml:
            self.actions = re.findall(r'<(.*?)[ /](.*?)/?>', xml.read())
            for action_i, (elem, attr) in enumerate(self.actions):
                self.action_i = action_i
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

                    # リーチの抽出
                    if self.mode == Format.RICHI_MODE:
                        self.sample_richi(who)

                # 打牌
                elif re.match(r'[D|E|F|G][0-9]+', elem):
                    idx = {'D': 0, 'E': 1, 'F': 2, 'G': 3}
                    who = idx[elem[0]]
                    pai = self.pai(int(elem[1:]))

                    # 打牌の抽出
                    if self.mode == Format.DAHAI_MODE and randint(1, 50) == 1:
                        self.output(who, pai)

                    # 打牌の処理
                    self.dahai[who][pai] += 1
                    self.tehai[who][pai] -= 1
                    self.last_dahai = pai

                    # ポンの抽出
                    if self.mode == Format.PON_MODE:
                        self.sample_pon(pai, who)

                    # チーの抽出
                    if self.mode == Format.CHI_MODE:
                        self.sample_chi(pai, who)

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
    mode=Format.RICHI_MODE,
    max_count=800000,
    debug=False
)
